"""
Continuous daemon runner for research_scanner.
Runs fetch -> process requests -> Curator export -> rebuild vault index in a continuous loop.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from typing import Dict, Any, Optional

from research_scanner import config
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

CURATOR_TASK_PROMPT = """You are Curator, part of an existing project called research_scanner. Read
rows from the fetched_items SQLite table where consumed_by_curator = 0, and
read current-priorities.md in the vault root for what Director currently
cares about. Decide which raw fetched items are worth promoting into real
Obsidian notes.

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


def get_curator_prompt() -> str:
    """
    Returns Curator's task prompt text from curator_prompt.md if available,
    otherwise falls back to CURATOR_TASK_PROMPT.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "curator_prompt.md")
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            logger.warning("Failed to read curator_prompt.md: %s", e)
    return CURATOR_TASK_PROMPT


def run_curator_export_step(vault_path: str = config.OBSIDIAN_VAULT_PATH) -> Optional[Dict[str, int]]:
    """
    Step 3: Writes Curator's task prompt to a temp file, invokes Curator via Antigravity CLI in headless mode,
    parses the JSON decision list, and passes it to export_from_curator_decisions().

    Logs quota/rate-limit errors distinctly ("QUOTA EXHAUSTED - Curator call skipped this cycle").
    If the CLI call fails or returns unparseable output, logs an ERROR and skips export.
    """
    prompt_text = get_curator_prompt()
    prompt_file_path = None
    decisions_file_path = None

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as pf:
            pf.write(prompt_text)
            prompt_file_path = pf.name

        cmd = ["antigravity", "-p", "--prompt-file", prompt_file_path, "--output-format", "json"]
        try:
            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            logger.error("Curator CLI call failed: 'antigravity' executable not found in PATH.")
            return None
        except Exception as exec_err:
            logger.error("Failed to execute Antigravity CLI: %s", exec_err)
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
            return None

        # Clean optional markdown codeblock delimiters
        if raw_output.startswith("```"):
            lines = raw_output.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_output = "\n".join(lines).strip()

        try:
            decisions = json.loads(raw_output)
            if isinstance(decisions, dict) and "decisions" in decisions:
                decisions = decisions["decisions"]
            if not isinstance(decisions, list):
                raise ValueError("Parsed JSON is not a list of decisions")
        except Exception as parse_err:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Curator call skipped this cycle")
            else:
                logger.error("Curator CLI output returned unparseable JSON: %s", parse_err)
            return None

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as df:
            json.dump(decisions, df)
            decisions_file_path = df.name

        export_stats = export_from_curator_decisions(decisions_file_path, vault_path=vault_path)
        logger.info("Obsidian export stats: %s", export_stats)
        return export_stats

    except Exception as e:
        logger.error("Unexpected error during Curator export step: %s", e, exc_info=True)
        return None
    finally:
        if prompt_file_path and os.path.exists(prompt_file_path):
            try:
                os.remove(prompt_file_path)
            except OSError:
                pass
        if decisions_file_path and os.path.exists(decisions_file_path):
            try:
                os.remove(decisions_file_path)
            except OSError:
                pass


def run_continuous_daemon(interval_seconds: int = 1800, vault_path: str = config.OBSIDIAN_VAULT_PATH) -> None:
    """
    Executes the research_scanner pipeline continuously every interval_seconds.

    :param interval_seconds: Time to sleep between scan iterations (default: 1800s / 30 min)
    :param vault_path: Path to target Obsidian vault
    """
    logger.info("==================================================")
    logger.info("   RESEARCH SCANNER CONTINUOUS DAEMON STARTED     ")
    logger.info("   Interval: %d seconds (%d minutes)            ", interval_seconds, interval_seconds // 60)
    logger.info("   Vault: %s                                      ", vault_path)
    logger.info("==================================================")

    iteration = 1
    while True:
        logger.info("--- Starting Cycle #%d at %s ---", iteration, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            # Step 1: Run raw fetch & deduplication cycle
            scan_stats = run_scan_cycle()
            logger.info("Scan cycle #%d stats: %s", iteration, scan_stats)

            # Step 2: Process queued director requests
            run_process_requests()

            # Step 3: Curator agent CLI evaluation & Obsidian export
            run_curator_export_step(vault_path=vault_path)

            # Step 4: Rebuild Obsidian vault index
            build_vault_index(vault_path)
            logger.info("Obsidian vault index rebuilt.")

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
    args = parser.parse_args()

    run_continuous_daemon(interval_seconds=args.interval, vault_path=args.vault)


if __name__ == "__main__":
    main()
