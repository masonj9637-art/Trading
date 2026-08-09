"""
Continuous daemon runner for research_scanner.
Runs fetch -> process requests -> Curator export -> rebuild vault index in a continuous loop.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from typing import Dict, Any, Optional

from research_scanner import config
from research_scanner.db import get_unconsumed_items, mark_items_reviewed
from research_scanner.scan import run_scan_cycle
from research_scanner.process_requests import run_process_requests
from research_scanner.export_to_obsidian import export_from_curator_decisions
from research_scanner.build_vault_index import build_vault_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("research_scanner.daemon")

CURATOR_TASK_PROMPT = """You are Curator, part of an existing project called research_scanner. Below are Director's current priorities and the current unconsumed fetched items. Decide which raw fetched items are worth promoting into real Obsidian notes.

Director's Current Priorities (current-priorities.md):
{priorities_text}

Here are the current unconsumed items:
{items_text}

Do NOT write files yourself. Output a JSON decision list - for each item
you're promoting: its fetched_items id, a normalized lowercase category
(reuse an existing theme category when the topic genuinely matches one,
don't invent near-duplicates), your reasoning tied explicitly to
current-priorities.md, and, if the item's request_id is set, which
escalation/theme note this finding supports and what specific claim it
addresses. A separate script (export_to_obsidian.py's new
export_from_curator_decisions function, Build 4) performs the actual file
writes and marks items consumed from your decision list.

Be a genuine filter, not a rubber stamp - a mechanical fetch of 200 arXiv
results is not 200 findings; most of it was never actually looked at by
anyone until now. Only include what you'd stand behind as worth Director's
or a human's time. Items you don't include in your decision list simply
remain unconsumed and unpromoted - still available in SQLite for audit, not
cluttering the vault."""


def is_quota_error(stderr: str = "", stdout: str = "", returncode: Optional[int] = None) -> bool:
    """
    Checks stderr, stdout, or error messages for quota or rate-limit specific indicators.
    """
    combined = (stderr + " " + stdout).lower()
    quota_keywords = [
        "quota",
        "rate limit",
        "ratelimit",
        "rate_limit",
        "resource_exhausted",
        "resourceexhausted",
        "429",
        "too many requests",
    ]
    return any(kw in combined for kw in quota_keywords)


def get_repo_root() -> str:
    """
    Determines the absolute path to the Trading repo root dynamically.
    Priority:
    1. TRADING_REPO_ROOT environment variable (if set)
    2. os.getcwd() if research_scanner exists in current working directory
    3. Parent directory of research_scanner package
    """
    if os.getenv("TRADING_REPO_ROOT"):
        return os.path.abspath(os.getenv("TRADING_REPO_ROOT"))
    if os.path.exists(os.path.join(os.getcwd(), "research_scanner")):
        return os.getcwd()
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_curator_prompt(
    db_path: str = config.DB_PATH,
    vault_path: str = config.OBSIDIAN_VAULT_PATH
) -> tuple[str, list[int]]:
    """
    Constructs the Curator prompt by loading the base prompt template,
    fetching unconsumed items directly from SQLite, and reading current-priorities.md
    from the vault root.
    Returns a tuple of (prompt_text, list_of_unconsumed_item_ids).
    """
    # 1. Fetch unconsumed items from DB
    try:
        unconsumed_items = get_unconsumed_items(db_path)
    except Exception as e:
        logger.warning("Failed to fetch unconsumed items from database %s: %s", db_path, e)
        unconsumed_items = []

    compact_items = []
    item_ids = []
    for item in unconsumed_items:
        i_id = item.get("id")
        if i_id is not None:
            item_ids.append(i_id)
        compact_items.append({
            "id": i_id,
            "source": item.get("source"),
            "title": item.get("title"),
            "summary": item.get("summary"),
            "url": item.get("url"),
            "fetched_at": str(item.get("fetched_at")) if item.get("fetched_at") is not None else None,
            "request_id": item.get("request_id"),
        })
    items_text = json.dumps(compact_items, indent=2)

    # 2. Read current-priorities.md from vault_path
    priorities_path = os.path.join(vault_path, "current-priorities.md")
    if os.path.exists(priorities_path):
        try:
            with open(priorities_path, "r", encoding="utf-8") as f:
                priorities_text = f.read().strip()
                if not priorities_text:
                    priorities_text = "(empty current-priorities.md)"
        except Exception as e:
            logger.warning("Failed to read current-priorities.md at %s: %s", priorities_path, e)
            priorities_text = "(Error reading current-priorities.md)"
    else:
        priorities_text = "(No current-priorities.md found in vault root)"

    # 3. Load base prompt template
    template = CURATOR_TASK_PROMPT
    prompt_path = os.path.join(os.path.dirname(__file__), "curator_prompt.md")
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    template = content
        except Exception as e:
            logger.warning("Failed to read curator_prompt.md: %s", e)

    if "{priorities_text}" in template and "{items_text}" in template:
        prompt_text = template.format(priorities_text=priorities_text, items_text=items_text)
    else:
        prompt_text = (
            f"{template}\n\n"
            f"Director's Current Priorities (current-priorities.md):\n{priorities_text}\n\n"
            f"Here are the current unconsumed items:\n{items_text}"
        )

    return prompt_text, item_ids


def get_agy_executable_path() -> str:
    """
    Returns the full absolute path to the agy executable.
    Priority:
    1. AGY_EXECUTABLE_PATH environment variable if set
    2. shutil.which("agy") or shutil.which("agy.exe")
    3. Fallback to confirmed path on this machine: C:\\Users\\mason\\AppData\\Local\\agy\\bin\\agy.exe
    """
    env_path = os.getenv("AGY_EXECUTABLE_PATH")
    if env_path:
        return env_path
    which_path = shutil.which("agy") or shutil.which("agy.exe")
    if which_path:
        return which_path
    return r"C:\Users\mason\AppData\Local\agy\bin\agy.exe"


def run_curator_export_step(
    vault_path: str = config.OBSIDIAN_VAULT_PATH,
    db_path: str = config.DB_PATH
) -> Optional[Dict[str, int]]:
    """
    Step 3: Invokes Curator via agy CLI in headless mode,
    parses the JSON decision list, and passes it to export_from_curator_decisions().

    Logs quota/rate-limit errors distinctly ("QUOTA EXHAUSTED - Curator call skipped this cycle").
    If the CLI call fails or returns unparseable output, logs an ERROR and skips export.
    """
    prompt_text, sent_item_ids = get_curator_prompt(db_path=db_path, vault_path=vault_path)
    repo_root = get_repo_root()
    agy_path = get_agy_executable_path()

    try:
        cmd = [agy_path, "--add-dir", repo_root, "--output-format", "json"]
        try:
            proc = subprocess.run(
                cmd,
                input=prompt_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except FileNotFoundError:
            logger.error("Curator CLI call failed: 'agy' executable not found at path '%s'.", agy_path)
            return None
        except Exception as exec_err:
            logger.error("Failed to execute agy CLI: %s", exec_err)
            return None

        if proc.returncode != 0:
            if is_quota_error(proc.stderr, proc.stdout, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Curator call skipped this cycle")
            else:
                logger.error(
                    "Curator CLI call failed with exit code %d: %s",
                    proc.returncode,
                    proc.stderr.strip() if proc.stderr else proc.stdout.strip(),
                )
            return None

        raw_output = proc.stdout.strip() if proc.stdout else ""
        if not raw_output:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Curator call skipped this cycle")
            else:
                logger.error("Curator CLI returned empty output.")
            logger.error("Curator CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return None

        # 1. Parse outer agy JSON envelope
        try:
            envelope = json.loads(raw_output)
        except Exception as envelope_err:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Curator call skipped this cycle")
            else:
                logger.error("Curator CLI output returned unparseable envelope JSON: %s", envelope_err)
            logger.error("Raw Curator output that failed to parse: %s", raw_output[:2000])
            logger.error("Curator CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return None

        # Extract inner response string from envelope
        if isinstance(envelope, dict) and "response" in envelope:
            inner_response = envelope["response"]
        elif isinstance(envelope, (list, dict)):
            # Direct fallback if raw output was raw JSON list/dict without response wrapper
            inner_response = raw_output
        else:
            inner_response = ""

        if not inner_response or not isinstance(inner_response, str):
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Curator call skipped this cycle")
            else:
                logger.error("Curator CLI response field is empty.")
            logger.error("Curator CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return None

        # Clean optional markdown codeblock delimiters from inner response
        inner_response_clean = inner_response.strip()
        if inner_response_clean.startswith("```"):
            lines = inner_response_clean.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            inner_response_clean = "\n".join(lines).strip()

        # 2. Parse inner response JSON into decision list
        try:
            decisions = json.loads(inner_response_clean)
            if isinstance(decisions, dict) and "decisions" in decisions:
                decisions = decisions["decisions"]
            if not isinstance(decisions, list):
                raise ValueError("Parsed JSON is not a list of decisions")
        except Exception as parse_err:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Curator call skipped this cycle")
            else:
                logger.error("Curator CLI inner response returned unparseable JSON: %s", parse_err)
            logger.error("Raw Curator output that failed to parse: %s", inner_response[:2000])
            logger.error("Curator CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return None

        decisions_file_path = "curator_decisions.json"
        with open(decisions_file_path, "w", encoding="utf-8") as df:
            json.dump(decisions, df, indent=2)

        export_stats = export_from_curator_decisions(decisions_file_path, db_path=db_path, vault_path=vault_path)
        logger.info("Obsidian export stats: %s", export_stats)

        promoted_item_ids = {
            d["fetched_item_id"]
            for d in decisions
            if isinstance(d, dict) and d.get("fetched_item_id") is not None
        }
        unpromoted_ids = [item_id for item_id in sent_item_ids if item_id not in promoted_item_ids]
        if unpromoted_ids:
            marked_count = mark_items_reviewed(db_path, unpromoted_ids)
            logger.info("Marked %d unpromoted item(s) as reviewed_not_promoted.", marked_count)

        return export_stats

    except Exception as e:
        logger.error("Unexpected error during Curator export step: %s", e, exc_info=True)
        return None


def update_last_success(
    key: str = "scan_and_curator",
    filepath: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> str:
    """
    Updates the shared last_success.json timestamp file for the specified key,
    preserving all existing keys.
    Returns the ISO 8601 timestamp string that was written.
    """
    target_path = filepath if filepath is not None else getattr(config, "LAST_SUCCESS_PATH", None)
    if not target_path:
        target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_success.json")

    data = {}
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        data = parsed
        except Exception as e:
            logger.warning("Failed to read existing last_success file at %s: %s", target_path, e)
            data = {}

    ts_str = timestamp if timestamp is not None else datetime.now().isoformat()
    data[key] = ts_str

    parent_dir = os.path.dirname(os.path.abspath(target_path))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return ts_str


def run_single_cycle(
    vault_path: str = config.OBSIDIAN_VAULT_PATH,
    db_path: str = config.DB_PATH,
    iteration: Optional[int] = None,
    last_success_path: Optional[str] = None,
) -> None:
    """
    Executes a single cycle of the research_scanner pipeline:
    1. Scan cycle (run_scan_cycle)
    2. Process requests (run_process_requests)
    3. Curator export (run_curator_export_step)
    4. Build vault index (build_vault_index)
    5. Update shared last_success.json timestamp for 'scan_and_curator'
    """
    iter_label = f" #{iteration}" if iteration is not None else ""
    logger.info("--- Starting Cycle%s at %s ---", iter_label, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Step 1: Run raw fetch & deduplication cycle
    scan_stats = run_scan_cycle(db_path=db_path)
    if iteration is not None:
        logger.info("Scan cycle #%d stats: %s", iteration, scan_stats)
    else:
        logger.info("Scan cycle stats: %s", scan_stats)

    # Step 2: Process queued director requests
    run_process_requests(db_path=db_path)

    # Step 3: Curator agent CLI evaluation & Obsidian export
    run_curator_export_step(vault_path=vault_path, db_path=db_path)

    # Step 4: Rebuild Obsidian vault index
    build_vault_index(vault_path)
    logger.info("Obsidian vault index rebuilt.")

    # Step 5: Update last_success timestamp
    try:
        ts = update_last_success("scan_and_curator", filepath=last_success_path)
        logger.info("Updated last_success.json with scan_and_curator timestamp: %s", ts)
    except Exception as e:
        logger.warning("Failed to update last_success.json: %s", e)



def run_continuous_daemon(
    interval_seconds: int = 1800,
    vault_path: str = config.OBSIDIAN_VAULT_PATH,
    db_path: str = config.DB_PATH,
) -> None:
    """
    Executes the research_scanner pipeline continuously every interval_seconds.

    :param interval_seconds: Time to sleep between scan iterations (default: 1800s / 30 min)
    :param vault_path: Path to target Obsidian vault
    :param db_path: Path to target SQLite database
    """
    logger.info("==================================================")
    logger.info("   RESEARCH SCANNER CONTINUOUS DAEMON STARTED     ")
    logger.info("   Interval: %d seconds (%d minutes)            ", interval_seconds, interval_seconds // 60)
    logger.info("   Vault: %s                                      ", vault_path)
    logger.info("==================================================")

    iteration = 1
    while True:
        try:
            run_single_cycle(vault_path=vault_path, db_path=db_path, iteration=iteration)
        except KeyboardInterrupt:
            logger.info("Daemon execution stopped by user (KeyboardInterrupt). Exiting.")
            sys.exit(0)
        except Exception as e:
            logger.error("Error during daemon cycle #%d: %s", iteration, e, exc_info=True)

        logger.info("Cycle #%d complete. Sleeping for %d seconds...", iteration, interval_seconds)
        time.sleep(interval_seconds)
        iteration += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuous background daemon for research_scanner.")
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="Scan interval in seconds (default: 1800 = 30 minutes)",
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=config.OBSIDIAN_VAULT_PATH,
        help=f"Target Obsidian vault path (default: {config.OBSIDIAN_VAULT_PATH})",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=config.DB_PATH,
        help=f"Target SQLite database path (default: {config.DB_PATH})",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run exactly one cycle of the pipeline and exit immediately.",
    )
    args = parser.parse_args()

    if args.once:
        run_single_cycle(vault_path=args.vault, db_path=args.db)
    else:
        run_continuous_daemon(interval_seconds=args.interval, vault_path=args.vault, db_path=args.db)


if __name__ == "__main__":
    main()


