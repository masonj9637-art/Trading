"""
Vault Index Builder for research_scanner.

Walks the Obsidian vault (OBSIDIAN_VAULT_PATH from config.py) for raw-signals/,
themes/, and audits/ folders and builds a single flat summary file (vault-index.md)
in the vault root.
"""

import argparse
import logging
import os
import re
import sys
from typing import Dict, Any, List, Optional

try:
    from research_scanner import config
except ImportError:
    import config

logger = logging.getLogger("research_scanner.build_vault_index")


def parse_yaml_frontmatter(content: str) -> Optional[Dict[str, str]]:
    """
    Parses key-value pairs from YAML frontmatter delimited by '---' at the start of a file.
    Returns dictionary of lowercase keys to stripped string values.
    Returns None if frontmatter is missing or malformed.
    """
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    yaml_block = parts[1].strip()
    if not yaml_block:
        return None

    frontmatter: Dict[str, str] = {}
    current_key = None
    for line in yaml_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current_key:
                val = line[2:].strip().strip("\"'")
                if current_key in frontmatter and frontmatter[current_key]:
                    frontmatter[current_key] += f", {val}"
                else:
                    frontmatter[current_key] = val
            continue
        if ":" not in line:
            return None
        key, val = line.split(":", 1)
        current_key = key.strip().lower()
        frontmatter[current_key] = val.strip().strip("\"'")

    return frontmatter


def extract_h1_title(body: str) -> Optional[str]:
    """
    Extracts title from the first H1 header in the note body.
    """
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def extract_first_sentence(text: str) -> str:
    """
    Extracts the first sentence from a block of text.
    """
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    
    # Match up to first period, exclamation mark, or question mark followed by space or end
    m = re.search(r"^(.*?[.!?])(?:\s|$)", cleaned)
    if m:
        return m.group(1).strip()
    return cleaned


def extract_gist(body: str, note_type: str) -> str:
    """
    Extracts a one-line deterministic gist from the note body based on note_type.
    - raw-signals: text from '## Curator Reasoning' section
    - audits: first sentence of 'Thesis Summary' section
    - themes / fallback: first sentence of note body after H1
    """
    if note_type == "raw-signals":
        m = re.search(r"##\s+Curator\s+Reasoning\s*\n+(.*?)(?=\n##|\n#|\n---|\Z)", body, re.DOTALL | re.IGNORECASE)
        if m:
            reason_text = m.group(1).strip()
            reason_clean = re.sub(r"\s+", " ", reason_text).strip()
            if reason_clean:
                return reason_clean
        body_no_h1 = re.sub(r"^#\s+.*$", "", body, flags=re.MULTILINE).strip()
        return extract_first_sentence(body_no_h1)

    elif note_type == "audits":
        m = re.search(r"(?:1\.\s*|##\s*)Thesis\s+Summary\s*\n+(.*?)(?=\n\d+\.|\n##|\n#|\n---|\Z)", body, re.DOTALL | re.IGNORECASE)
        if m:
            summary_text = m.group(1).strip()
            return extract_first_sentence(summary_text)
        body_no_h1 = re.sub(r"^#\s+.*$", "", body, flags=re.MULTILINE).strip()
        return extract_first_sentence(body_no_h1)

    else:  # themes or general
        body_no_h1 = re.sub(r"^#\s+.*$", "", body, flags=re.MULTILINE).strip()
        lines = [line.strip() for line in body_no_h1.splitlines() if line.strip() and not line.strip().startswith("#")]
        if lines:
            first_block = " ".join(lines)
            return extract_first_sentence(first_block)
        return "No summary provided."


def parse_note(file_path: str, rel_path: str, note_type: str) -> Optional[Dict[str, Any]]:
    """
    Parses a single note file. Returns metadata dictionary or None if frontmatter is missing/malformed.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.warning("Skipping note %s: could not read file (%s)", file_path, e)
        return None

    fm = parse_yaml_frontmatter(content)
    if fm is None:
        logger.warning("Skipping note %s: missing or malformed YAML frontmatter", file_path)
        return None

    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else ""

    title = extract_h1_title(body)
    if not title:
        title = fm.get("title", "")
    if not title:
        title = os.path.splitext(os.path.basename(file_path))[0]

    if note_type == "raw-signals":
        category = fm.get("category") or fm.get("theme") or "Uncategorized"
    elif note_type == "audits":
        category = fm.get("theme_note") or fm.get("category") or fm.get("theme") or "General"
    else:  # themes
        category = fm.get("category") or fm.get("theme") or title

    status = fm.get("status", "N/A")

    if note_type == "raw-signals":
        raw_date = fm.get("fetched_at") or fm.get("created_at") or fm.get("date") or "N/A"
    elif note_type == "audits":
        raw_date = fm.get("audit_date") or fm.get("created_at") or fm.get("date") or "N/A"
    else:  # themes
        raw_date = fm.get("created_at") or fm.get("date") or fm.get("updated_at") or "N/A"
    date_str = str(raw_date)[:10] if raw_date != "N/A" else "N/A"

    gist = extract_gist(body, note_type)

    entry: Dict[str, Any] = {
        "rel_path": rel_path.replace("\\", "/"),
        "title": title,
        "category": category,
        "status": status,
        "date": date_str,
        "gist": gist,
        "note_type": note_type,
    }

    if note_type == "audits":
        fact_check_match = re.search(r"##\s+(?:Independent\s+)?Fact[- ]Check", body, re.IGNORECASE)
        if fact_check_match:
            post_header_text = body[fact_check_match.end():].strip()
            if post_header_text:
                confidence = fm.get("confidence_level")
                if not confidence:
                    m_conf = re.search(r"Confidence(?:\s+Level)?[*:\s]+([^\n\r]+)", body, re.IGNORECASE)
                    confidence = m_conf.group(1).replace('*', '').strip() if m_conf else "N/A"
                
                verdict = fm.get("fact_check_verdict")
                if not verdict:
                    m_verd = re.search(
                        r"Verdict[*:\s]+(claims well-supported|some claims overstated|claims not well-supported by sources)",
                        body,
                        re.IGNORECASE,
                    )
                    if m_verd:
                        verdict = m_verd.group(1).strip().lower()
                    else:
                        sec_lower = post_header_text.lower()
                        if "overstated" in sec_lower:
                            verdict = "some claims overstated"
                        elif "not well-supported" in sec_lower or "not well supported" in sec_lower:
                            verdict = "claims not well-supported by sources"
                        elif "well-supported" in sec_lower or "well supported" in sec_lower:
                            verdict = "claims well-supported"
                        else:
                            verdict = "N/A"
                
                entry["confidence_level"] = confidence
                entry["fact_check_verdict"] = verdict

    return entry


def build_vault_index(vault_path: str = config.OBSIDIAN_VAULT_PATH) -> str:
    """
    Scans the vault folder for raw-signals/, themes/, and audits/ notes,
    parses metadata and deterministic gists, and writes vault-index.md to vault root.

    :param vault_path: Path to Obsidian vault directory
    :return: Path to created vault-index.md file
    """
    if not os.path.exists(vault_path):
        os.makedirs(vault_path, exist_ok=True)

    grouped_entries: Dict[str, List[Dict[str, Any]]] = {
        "Raw Signals": [],
        "Themes": [],
        "Audits": [],
    }

    folder_map = [
        ("raw-signals", "Raw Signals", "raw-signals"),
        ("themes", "Themes", "themes"),
        ("audits", "Audits", "audits"),
    ]

    for dir_name, group_key, note_type in folder_map:
        target_dir = os.path.join(vault_path, dir_name)
        if not os.path.exists(target_dir):
            continue

        for root, _, files in os.walk(target_dir):
            for file in files:
                if not file.endswith(".md"):
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, vault_path)

                parsed = parse_note(file_path, rel_path, note_type)
                if parsed:
                    grouped_entries[group_key].append(parsed)

    for group_key in grouped_entries:
        grouped_entries[group_key].sort(key=lambda x: (x["date"], x["rel_path"]))

    index_lines = ["# Vault Index\n"]

    for group_name in ["Raw Signals", "Themes", "Audits"]:
        index_lines.append(f"## {group_name}")
        entries = grouped_entries[group_name]
        for e in entries:
            if "confidence_level" in e and "fact_check_verdict" in e:
                line = (
                    f"- [{e['rel_path']}] Title: {e['title']} | Theme: {e['category']} | "
                    f"Status: {e['status']} | Date: {e['date']} | "
                    f"Confidence: {e['confidence_level']} | Verdict: {e['fact_check_verdict']} | "
                    f"Gist: {e['gist']}"
                )
            else:
                cat_label = "Category" if group_name == "Raw Signals" else "Theme"
                line = (
                    f"- [{e['rel_path']}] Title: {e['title']} | {cat_label}: {e['category']} | "
                    f"Status: {e['status']} | Date: {e['date']} | "
                    f"Gist: {e['gist']}"
                )
            index_lines.append(line)
        index_lines.append("")

    content = "\n".join(index_lines).strip() + "\n"
    index_file_path = os.path.join(vault_path, "vault-index.md")

    with open(index_file_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("Successfully built vault index at %s", index_file_path)
    return index_file_path


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    parser = argparse.ArgumentParser(
        description="Build vault-index.md summary file from raw-signals, themes, and audits in the Obsidian vault."
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=config.OBSIDIAN_VAULT_PATH,
        help=f"Path to Obsidian vault folder (default: {config.OBSIDIAN_VAULT_PATH})",
    )

    args = parser.parse_args()
    build_vault_index(vault_path=args.vault)


if __name__ == "__main__":
    main()
