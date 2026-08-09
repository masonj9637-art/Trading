"""
director_run.py

Director execution runner module for research_scanner.
Invokes Director via agy CLI, parses output envelope, validates schema,
writes director_output.json, invokes director_apply logic directly,
and updates shared last_success.json timestamp on success.
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# Ensure parent directory is in sys.path when run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from research_scanner import config
from research_scanner.director_apply import apply_director_output
from research_scanner.run_daemon import get_agy_executable_path, get_repo_root, is_quota_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("research_scanner.director_run")


def get_director_prompt(
    vault_path: Optional[str] = None,
    context_path: Optional[str] = None,
    prompt_path: Optional[str] = None,
) -> str:
    """
    Constructs Director prompt by loading vault-index.md, current-priorities.md,
    and all files in research_scanner/context/, embedding them into director_prompt.md template.
    """
    repo_root = get_repo_root()
    if vault_path is None:
        vault_path = config.OBSIDIAN_VAULT_PATH
    if context_path is None:
        context_path = os.path.join(repo_root, "research_scanner", "context")
    if prompt_path is None:
        prompt_path = os.path.join(os.path.dirname(__file__), "director_prompt.md")

    # 1. Read vault-index.md
    vault_index_file = os.path.join(vault_path, "vault-index.md")
    if os.path.exists(vault_index_file):
        try:
            with open(vault_index_file, "r", encoding="utf-8") as f:
                vault_index_text = f.read().strip()
                if not vault_index_text:
                    vault_index_text = "(empty vault-index.md)"
        except Exception as e:
            logger.warning("Failed to read vault-index.md at %s: %s", vault_index_file, e)
            vault_index_text = "(Error reading vault-index.md)"
    else:
        vault_index_text = "(No vault-index.md found in vault root)"

    # 2. Read current-priorities.md
    priorities_file = os.path.join(vault_path, "current-priorities.md")
    if os.path.exists(priorities_file):
        try:
            with open(priorities_file, "r", encoding="utf-8") as f:
                priorities_text = f.read().strip()
                if not priorities_text:
                    priorities_text = "(empty current-priorities.md)"
        except Exception as e:
            logger.warning("Failed to read current-priorities.md at %s: %s", priorities_file, e)
            priorities_text = "(Error reading current-priorities.md)"
    else:
        priorities_text = "(No current-priorities.md found in vault root)"

    # 3. Read files in context_path gracefully
    context_blocks = []
    if context_path and os.path.exists(context_path) and os.path.isdir(context_path):
        try:
            filenames = sorted(os.listdir(context_path))
            for filename in filenames:
                file_p = os.path.join(context_path, filename)
                if os.path.isfile(file_p):
                    try:
                        with open(file_p, "r", encoding="utf-8") as f:
                            c_content = f.read().strip()
                            if not c_content:
                                c_content = "(empty file)"
                            context_blocks.append(f"--- {filename} ---\n{c_content}")
                    except Exception as e:
                        logger.warning("Failed to read context file %s: %s", file_p, e)
                        context_blocks.append(f"--- {filename} ---\n(Error reading file)")
        except Exception as e:
            logger.warning("Failed to list context directory %s: %s", context_path, e)

    if context_blocks:
        context_text = "\n\n".join(context_blocks)
    else:
        context_text = "(No context files present)"

    # 4. Load template prompt
    template = ""
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                template = f.read().strip()
        except Exception as e:
            logger.warning("Failed to read director_prompt.md: %s", e)

    if "{vault_index_text}" in template or "{priorities_text}" in template or "{context_text}" in template:
        prompt_text = (
            template.replace("{vault_index_text}", vault_index_text)
            .replace("{priorities_text}", priorities_text)
            .replace("{context_text}", context_text)
        )
    else:
        prompt_text = (
            f"{template}\n\n"
            f"Vault INDEX (vault-index.md):\n{vault_index_text}\n\n"
            f"Director's Current Priorities (current-priorities.md):\n{priorities_text}\n\n"
            f"Context Files (context/):\n{context_text}\n\n"
            f"The vault index, priorities, and context provided above are complete and current — do NOT attempt to query the database, read additional files, or run any commands to verify or supplement this information. Everything needed for this decision has already been given to you."
        )

    return prompt_text


def validate_director_output(data: Any) -> bool:
    """
    Validates that parsed JSON is a dict matching Director's expected schema.
    Optional keys: updated_priorities (str), fetch_requests (list), escalation (dict), proactive_message (str).
    """
    if not isinstance(data, dict):
        logger.error("Director JSON output root must be a dict/object, got %s", type(data).__name__)
        return False

    if "updated_priorities" in data and data["updated_priorities"] is not None:
        if not isinstance(data["updated_priorities"], str):
            logger.error("Schema validation failed: updated_priorities must be a string")
            return False

    if "fetch_requests" in data and data["fetch_requests"] is not None:
        if not isinstance(data["fetch_requests"], list):
            logger.error("Schema validation failed: fetch_requests must be a list")
            return False

    if "escalation" in data and data["escalation"] is not None:
        if not isinstance(data["escalation"], dict):
            logger.error("Schema validation failed: escalation must be a dict/object")
            return False

    if "proactive_message" in data and data["proactive_message"] is not None:
        if not isinstance(data["proactive_message"], str):
            logger.error("Schema validation failed: proactive_message must be a string")
            return False

    return True


def update_last_success_timestamp(
    timestamp_path: Optional[str] = None, key: str = "director"
) -> None:
    """
    Updates the shared timestamp file at timestamp_path with the current ISO 8601 timestamp for `key`.
    Creates file if missing, preserves existing keys.
    """
    if timestamp_path is None:
        timestamp_path = os.path.join(get_repo_root(), "research_scanner", "last_success.json")

    data = {}
    if os.path.exists(timestamp_path):
        try:
            with open(timestamp_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    existing_data = json.loads(content)
                    if isinstance(existing_data, dict):
                        data = existing_data
        except Exception as e:
            logger.warning("Failed to read existing %s: %s", timestamp_path, e)

    data[key] = datetime.now().astimezone().isoformat()

    parent_dir = os.path.dirname(os.path.abspath(timestamp_path))
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(timestamp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_director_step(
    vault_path: Optional[str] = None,
    db_path: Optional[str] = None,
    context_path: Optional[str] = None,
    output_path: str = "director_output.json",
    timestamp_path: Optional[str] = None,
) -> bool:
    """
    Invokes Director via agy CLI, parses and validates output JSON,
    writes director_output.json, invokes apply_director_output logic directly,
    and updates last_success.json on success.
    """
    if vault_path is None:
        vault_path = config.OBSIDIAN_VAULT_PATH
    if db_path is None:
        db_path = config.DB_PATH
    if context_path is None:
        context_path = os.path.join(get_repo_root(), "research_scanner", "context")
    if timestamp_path is None:
        timestamp_path = os.path.join(get_repo_root(), "research_scanner", "last_success.json")

    prompt_text = get_director_prompt(vault_path=vault_path, context_path=context_path)
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
            logger.error("Director CLI call failed: 'agy' executable not found at path '%s'.", agy_path)
            return False
        except Exception as exec_err:
            logger.error("Failed to execute agy CLI: %s", exec_err)
            return False

        if proc.returncode != 0:
            if is_quota_error(proc.stderr, proc.stdout, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Director call skipped this cycle")
            else:
                logger.error(
                    "Director CLI call failed with exit code %d: %s",
                    proc.returncode,
                    proc.stderr.strip() if proc.stderr else proc.stdout.strip(),
                )
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        raw_output = proc.stdout.strip() if proc.stdout else ""
        if not raw_output:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Director call skipped this cycle")
            else:
                logger.error("Director CLI returned empty output.")
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        # Parse outer agy JSON envelope
        try:
            envelope = json.loads(raw_output)
        except Exception as envelope_err:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Director call skipped this cycle")
            else:
                logger.error("Director CLI output returned unparseable envelope JSON: %s", envelope_err)
            logger.error("Raw Director output that failed to parse: %s", raw_output[:2000])
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        if isinstance(envelope, dict) and "response" in envelope:
            inner_response = envelope["response"]
        elif isinstance(envelope, (list, dict)):
            inner_response = raw_output
        else:
            inner_response = ""

        if not inner_response or not isinstance(inner_response, str):
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Director call skipped this cycle")
            else:
                logger.error("Director CLI response field is empty.")
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        # Clean optional markdown codeblock delimiters
        inner_response_clean = inner_response.strip()
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", inner_response_clean, re.DOTALL | re.IGNORECASE)
        if match:
            inner_response_clean = match.group(1).strip()

        # Parse inner response JSON
        try:
            parsed_json = json.loads(inner_response_clean)
        except Exception as parse_err:
            if is_quota_error(proc.stderr, raw_output, proc.returncode):
                logger.error("QUOTA EXHAUSTED - Director call skipped this cycle")
            else:
                logger.error("Director CLI inner response returned unparseable JSON: %s", parse_err)
            logger.error("Raw Director output that failed to parse: %s", inner_response[:2000])
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        # Validate schema
        if not validate_director_output(parsed_json):
            logger.error("Director CLI output failed schema validation.")
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        # Write fixed output JSON file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, indent=2)
            logger.info("Wrote Director output to %s", output_path)
        except Exception as write_err:
            logger.error("Failed to write Director output to %s: %s", output_path, write_err)
            logger.error("Director CLI stderr: %s", proc.stderr[:2000] if proc.stderr else "(empty)")
            return False

        # Apply output directly in python process
        apply_success = apply_director_output(output_path, vault_path=vault_path, db_path=db_path)
        if not apply_success:
            logger.error("apply_director_output failed to apply Director's decisions.")
            return False

        # Update last_success timestamp
        update_last_success_timestamp(timestamp_path=timestamp_path, key="director")
        logger.info("Successfully updated Director timestamp in %s", timestamp_path)
        return True

    except Exception as e:
        logger.error("Unexpected error during Director step: %s", e, exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Director step for research_scanner.")
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
        "--output",
        type=str,
        default="director_output.json",
        help="Path for Director JSON output (default: director_output.json)",
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Path to context directory",
    )
    parser.add_argument(
        "--timestamp-path",
        type=str,
        default=None,
        help="Path to last_success.json file",
    )
    args = parser.parse_args()

    success = run_director_step(
        vault_path=args.vault,
        db_path=args.db,
        context_path=args.context,
        output_path=args.output,
        timestamp_path=args.timestamp_path,
    )
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
