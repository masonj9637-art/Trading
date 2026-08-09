"""
director_apply.py

Applies Director's JSON output deterministically.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import shutil
from typing import Optional

# Ensure the parent directory is in sys.path so 'from research_scanner import ...' works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research_scanner import config
from research_scanner.db import get_db_connection, init_db
from research_scanner.notifier import send_discord_message

logger = logging.getLogger("research_scanner.director_apply")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def apply_director_output(
    input_path: str,
    vault_path: Optional[str] = None,
    db_path: Optional[str] = None
) -> bool:
    if vault_path is None:
        vault_path = config.OBSIDIAN_VAULT_PATH
    if db_path is None:
        db_path = config.DB_PATH

    if not os.path.exists(input_path):
        logger.error("Input file not found: %s", input_path)
        return False
        
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON input from %s. Error: %s", input_path, e)
            logger.error("Raw content:\n%s", content)
            return False
            
    except Exception as e:
        logger.error("Failed to read input file: %s", e)
        return False
        
    if not isinstance(data, dict):
        logger.error("JSON root must be an object/dict")
        return False
        
    # Handle agy CLI JSON envelope format: {"conversation_id": ..., "status": ..., "response": "<inner JSON string>"}
    director_keys = ("updated_priorities", "fetch_requests", "escalation", "proactive_message")
    if "response" in data and not any(k in data for k in director_keys):
        inner_response = data.get("response")
        if not inner_response or not isinstance(inner_response, str):
            logger.error("Director envelope response field is empty or not a string.")
            return False
            
        inner_response_clean = inner_response.strip()
        if inner_response_clean.startswith("```"):
            lines = inner_response_clean.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            inner_response_clean = "\n".join(lines).strip()
            
        try:
            data = json.loads(inner_response_clean)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse inner JSON response in Director envelope from %s. Error: %s", input_path, e)
            logger.error("Inner response content:\n%s", inner_response)
            return False
            
        if not isinstance(data, dict):
            logger.error("Unwrapped inner Director JSON root must be an object/dict")
            return False
        
    logger.info("Successfully parsed Director JSON output from %s", input_path)
    
    updated_priorities = data.get("updated_priorities")
    fetch_requests = data.get("fetch_requests")
    escalation = data.get("escalation")
    proactive_message = data.get("proactive_message")

    # 1. Update priorities
    if updated_priorities is not None:
        if not isinstance(updated_priorities, str):
            logger.error("updated_priorities must be a string")
            return False
            
        priorities_file = os.path.join(vault_path, "current-priorities.md")
        
        # Ensure vault dir exists
        os.makedirs(vault_path, exist_ok=True)
        
        # Backup if exists
        if os.path.exists(priorities_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{priorities_file}.bak_{timestamp}"
            try:
                shutil.copy2(priorities_file, backup_file)
                logger.info("Backed up existing current-priorities.md to %s", backup_file)
            except Exception as e:
                logger.error("Failed to backup %s: %s", priorities_file, e)
                return False
                
        # Write new priorities
        try:
            with open(priorities_file, 'w', encoding='utf-8') as f:
                f.write(updated_priorities)
            logger.info("Updated current-priorities.md in vault root")
        except Exception as e:
            logger.error("Failed to write updated_priorities to %s: %s", priorities_file, e)
            return False

    # 2. Process fetch requests
    if fetch_requests is not None:
        if not isinstance(fetch_requests, list):
            logger.error("fetch_requests must be a list")
            return False
            
        inserted_count = 0
        try:
            init_db(db_path)
            conn = get_db_connection(db_path)
            with conn:
                for req in fetch_requests:
                    if not isinstance(req, dict):
                        continue
                    query = req.get("query", "")
                    source_hint = req.get("source_hint", "")
                    conn.execute(
                        "INSERT INTO director_requests (query, source_hint, status) VALUES (?, ?, ?)",
                        (query, source_hint, "pending")
                    )
                    inserted_count += 1
            logger.info("Queued %d fetch_requests", inserted_count)
        except Exception as e:
            logger.error("Database error while inserting fetch_requests: %s", e)
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    # 3. Handle escalation
    if escalation is not None:
        if not isinstance(escalation, dict):
            logger.error("escalation must be an object/dict")
            return False
            
        theme = escalation.get("theme", "No Theme")
        message = escalation.get("message", "")
        vault_note_path = escalation.get("vault_note_path")
        
        discord_msg = f"**Escalation**: {theme}\n{message}"
        if vault_note_path:
            discord_msg += f"\n*See note:* `{vault_note_path}`"
            full_note_path = os.path.join(vault_path, vault_note_path)
            if os.path.exists(full_note_path):
                try:
                    with open(full_note_path, 'r', encoding='utf-8') as nf:
                        note_content = nf.read()
                    
                    if "status: triaged" in note_content:
                        note_content = note_content.replace("status: triaged", "status: escalated")
                    elif "status:" not in note_content and note_content.startswith("---"):
                        note_content = note_content.replace("---\n", "---\nstatus: escalated\n", 1)

                    if "tags:" not in note_content and note_content.startswith("---"):
                        parts = note_content.split("---\n", 2)
                        if len(parts) >= 3:
                            note_content = f"---\n{parts[1].strip()}\ntags:\n  - escalated\n  - escalation\n---\n{parts[2]}"
                    elif "tags:" in note_content and "escalated" not in note_content:
                        note_content = note_content.replace("tags:\n", "tags:\n  - escalated\n  - escalation\n", 1)

                    with open(full_note_path, 'w', encoding='utf-8') as nf:
                        nf.write(note_content)
                    logger.info("Updated note frontmatter to status: escalated in %s", full_note_path)
                except Exception as e:
                    logger.error("Failed to update note frontmatter at %s: %s", full_note_path, e)
            
        if send_discord_message(discord_msg):
            logger.info("Sent escalation message to Discord")
        else:
            logger.error("Failed to send escalation message to Discord")
            
    # 4. Handle proactive message (only if escalation is not present)
    elif proactive_message is not None:
        if not isinstance(proactive_message, str):
            logger.error("proactive_message must be a string")
            return False
            
        if send_discord_message(proactive_message):
            logger.info("Sent proactive_message to Discord")
        else:
            logger.error("Failed to send proactive_message to Discord")

    logger.info("Director output applied successfully.")
    return True


def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Apply Director's JSON output")
    parser.add_argument("--input", required=True, help="Path to the Director JSON output file")
    args = parser.parse_args()
    
    success = apply_director_output(args.input)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
