"""
Thesis Ledger Scanner for research_scanner.
Scans Obsidian vault notes containing completed '## Independent Fact-Check' sections
and writes immutable audit records to the thesis_ledger SQLite table.
"""

import argparse
import hashlib
import logging
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from research_scanner import config
from research_scanner.db import (
    init_db,
    save_thesis_ledger_entry,
    get_all_ledger_entries,
)

logger = logging.getLogger("research_scanner.thesis_ledger")


def compute_ledger_hash(vault_note_path: str) -> str:
    """
    Computes a SHA256 hash derived from the vault note path for immutable deduplication.
    """
    rel_path = os.path.normpath(vault_note_path).strip()
    return hashlib.sha256(rel_path.encode("utf-8")).hexdigest()


def parse_yaml_frontmatter(content: str) -> Dict[str, str]:
    """
    Parses key-value pairs from simple YAML frontmatter delimited by '---'.
    """
    frontmatter: Dict[str, str] = {}
    if not content.startswith("---"):
        return frontmatter

    parts = content.split("---", 2)
    if len(parts) < 3:
        return frontmatter

    yaml_block = parts[1]
    for line in yaml_block.strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            frontmatter[key.strip().lower()] = val.strip().strip("\"'")

    return frontmatter


def parse_fact_check_note(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parses an Obsidian markdown note. If it contains a completed '## Independent Fact-Check'
    section, extracts ticker, audit_date, confidence_level, fact_check_verdict, and theme_note.
    Returns dictionary or None if incomplete/not a fact-check note.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error("Could not read note at %s: %s", file_path, e)
        return None

    # Check for Independent Fact-Check section header
    fact_check_match = re.search(r"##\s+(?:Independent\s+)?Fact[- ]Check", content, re.IGNORECASE)
    if not fact_check_match:
        return None

    # Check that section is completed (has content below header)
    post_header_text = content[fact_check_match.end() :].strip()
    if not post_header_text:
        return None

    fm = parse_yaml_frontmatter(content)

    # 1. Ticker extraction (frontmatter or body regex)
    ticker = fm.get("ticker", "")
    if not ticker:
        m = re.search(r"(?:\*\*Ticker\*\*|Ticker):\s*([A-Za-z0-9\.\-]+)", content, re.IGNORECASE)
        if m:
            ticker = m.group(1)
        else:
            # Fallback regex for standalone ticker symbols e.g. $NVDA or NVDA in body
            m2 = re.search(r"\$([A-Z]{1,5})\b", content)
            if m2:
                ticker = m2.group(1)

    if not ticker:
        ticker = "UNKNOWN"

    # 2. Audit date extraction
    audit_date = fm.get("audit_date") or fm.get("created_at") or ""
    if audit_date:
        audit_date = str(audit_date)[:10]
    else:
        m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", content)
        if m:
            audit_date = m.group(1)
        else:
            # File modification date as fallback
            mtime = os.path.getmtime(file_path)
            audit_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    # 3. Confidence level extraction
    confidence_level = fm.get("confidence_level") or fm.get("confidence") or ""
    if not confidence_level:
        m = re.search(r"(?:\*\*Confidence\*\*|Confidence):\s*([A-Za-z0-9\s]+)", content, re.IGNORECASE)
        if m:
            confidence_level = m.group(1).strip()
        else:
            confidence_level = "Medium"

    # 4. Fact check verdict extraction
    fact_check_verdict = fm.get("fact_check_verdict") or fm.get("verdict") or ""
    if not fact_check_verdict:
        m = re.search(r"(?:\*\*Verdict\*\*|Verdict):\s*([A-Za-z0-9\s]+)", content, re.IGNORECASE)
        if m:
            fact_check_verdict = m.group(1).strip()
        else:
            # Infer verdict keyword from section text
            sec_lower = post_header_text.lower()[:300]
            if "verified" in sec_lower or "confirmed" in sec_lower or "supported" in sec_lower:
                fact_check_verdict = "Supported"
            elif "refuted" in sec_lower or "debunked" in sec_lower or "false" in sec_lower:
                fact_check_verdict = "Refuted"
            else:
                fact_check_verdict = "Inconclusive"

    # 5. Theme note extraction
    theme_note = fm.get("theme_note") or fm.get("category") or ""
    if not theme_note:
        # Search for [[wikilink]] in note body
        m = re.search(r"\[\[([^\]]+)\]\]", content)
        if m:
            theme_note = m.group(1).strip()
        else:
            theme_note = "General Research"

    ledger_hash = compute_ledger_hash(file_path)

    return {
        "ledger_hash": ledger_hash,
        "ticker": ticker.upper(),
        "audit_date": audit_date,
        "confidence_level": confidence_level,
        "fact_check_verdict": fact_check_verdict,
        "theme_note": theme_note,
        "vault_note_path": file_path,
    }


def scan_vault_and_update_ledger(
    vault_path: str = config.OBSIDIAN_VAULT_PATH, db_path: str = config.DB_PATH
) -> Dict[str, int]:
    """
    Scans the Obsidian vault for audit notes with completed fact-check sections,
    extracts metadata, and writes immutable records to the thesis_ledger table.

    :return: Summary statistics dictionary
    """
    init_db(db_path)

    if not os.path.exists(vault_path):
        logger.warning("Obsidian vault directory %s does not exist. Skipping ledger scan.", vault_path)
        return {"scanned": 0, "added": 0, "existing": 0}

    stats = {"scanned": 0, "added": 0, "existing": 0}

    for root, _, files in os.walk(vault_path):
        for file in files:
            if not file.endswith(".md"):
                continue

            stats["scanned"] += 1
            file_path = os.path.join(root, file)

            parsed = parse_fact_check_note(file_path)
            if parsed is None:
                continue

            saved = save_thesis_ledger_entry(db_path, parsed)
            if saved:
                stats["added"] += 1
            else:
                stats["existing"] += 1

    logger.info(
        "Vault thesis ledger scan complete. Stats: Scanned=%d | Added=%d | Existing=%d",
        stats["scanned"],
        stats["added"],
        stats["existing"],
    )
    return stats


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    parser = argparse.ArgumentParser(
        description="Scan Obsidian vault for completed fact-check audit notes and log immutable records to thesis_ledger."
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=config.OBSIDIAN_VAULT_PATH,
        help=f"Path to Obsidian vault folder (default: {config.OBSIDIAN_VAULT_PATH})",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=config.DB_PATH,
        help=f"Path to SQLite database (default: {config.DB_PATH})",
    )

    args = parser.parse_args()
    scan_vault_and_update_ledger(vault_path=args.vault, db_path=args.db)


if __name__ == "__main__":
    main()
