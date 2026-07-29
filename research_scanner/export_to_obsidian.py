"""
Obsidian export module for research_scanner.
Exports unreviewed candidates from SQLite to Markdown files in an Obsidian vault.
"""

import argparse
import logging
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from research_scanner import config
from research_scanner.db import (
    init_db,
    get_unreviewed_candidates,
    mark_candidate_reviewed,
)

logger = logging.getLogger("research_scanner.export_to_obsidian")


def slugify_title(title: str, max_length: int = 60) -> str:
    """
    Converts a title string into a lowercase URL/file-friendly slug.
    """
    text = title.lower()
    # Replace non-alphanumeric characters (excluding spaces and hyphens) with empty string
    text = re.sub(r"[^\w\s-]", "", text)
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Strip leading/trailing hyphens
    slug = text.strip("-")
    if not slug:
        slug = "untitled"
    if len(slug) > max_length:
        # Truncate at hyphen boundary if possible
        truncated = slug[:max_length]
        if "-" in truncated:
            slug = truncated.rsplit("-", 1)[0]
        else:
            slug = truncated
    return slug


def get_folder_for_source(source: str) -> str:
    """
    Maps source string to subfolder path relative to vault root.
    """
    src_lower = source.strip().lower()
    if src_lower == "arxiv":
        return os.path.join("raw-signals", "arxiv")
    elif src_lower in ("uspto", "patent", "patents"):
        return os.path.join("raw-signals", "patents")
    elif src_lower in ("currents", "news"):
        return os.path.join("raw-signals", "news")
    else:
        return os.path.join("raw-signals", "other")


def format_theme_title(category: str) -> str:
    """
    Formats category tag into canonical Theme Title (e.g. 'quantum computing' -> 'Quantum Computing').
    """
    if not category or category.strip().lower() == "uncategorized":
        return "General Technology"

    words = category.strip().split()
    formatted_words = []
    for w in words:
        if w.lower() in ("and", "&"):
            formatted_words.append("&")
        elif w.lower() == "ai":
            formatted_words.append("AI")
        else:
            formatted_words.append(w.capitalize())
    return " ".join(formatted_words)


def ensure_theme_note_exists(vault_path: str, category: str) -> str:
    """
    Ensures a theme note file exists in the vault under themes/ (or vault root).
    Returns the theme note title string suitable for [[wikilink]].
    """
    theme_title = format_theme_title(category)
    themes_dir = os.path.join(vault_path, "themes")
    os.makedirs(themes_dir, exist_ok=True)

    theme_file_path = os.path.join(themes_dir, f"{theme_title}.md")
    if not os.path.exists(theme_file_path):
        try:
            content = (
                f"# {theme_title}\n\n"
                f"Automated theme note collecting research papers, patents, and news signals tagged with category `{category}`.\n\n"
                f"## Related Signals\n"
            )
            with open(theme_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info("Created theme note at %s", theme_file_path)
        except Exception as e:
            logger.error("Failed to create theme note at %s: %s", theme_file_path, e)

    return theme_title


def generate_candidate_note_content(candidate: Dict[str, Any], theme_title: str) -> str:
    """
    Generates Markdown content for a candidate item with YAML frontmatter, wikilinks, and sections.
    """
    score = candidate.get("score", 0.0)
    source = candidate.get("source", "unknown")
    category = candidate.get("category", "uncategorized")
    created_at = candidate.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = candidate.get("title", "Untitled").strip()
    url = candidate.get("url", "").strip()
    reason = candidate.get("reason", "No reason provided.").strip()
    summary = candidate.get("summary", "No summary provided.").strip()

    frontmatter = (
        "---\n"
        f"score: {score:.1f}\n"
        f"source: {source}\n"
        f"category: {category}\n"
        f"created_at: {created_at}\n"
        "status: triaged\n"
        "---\n\n"
    )

    url_line = f"[{url}]({url})" if url else "N/A"

    body = (
        f"# {title}\n\n"
        f"- **Triage Score**: {score:.1f}/10\n"
        f"- **Category Theme**: [[{theme_title}]]\n"
        f"- **Source**: {source.upper()}\n"
        f"- **Original URL**: {url_line}\n\n"
        f"## Gemma Triage Reason\n\n"
        f"{reason}\n\n"
        f"## Summary / Abstract\n\n"
        f"{summary}\n\n"
        f"## My Notes\n"
    )

    return frontmatter + body


def export_candidate_to_vault(candidate: Dict[str, Any], vault_path: str) -> str:
    """
    Writes a single candidate note to the appropriate vault subfolder.
    Handles filename collisions by appending a numeric suffix.

    :return: Absolute file path of exported note
    :raises IOError: If file write fails
    """
    # 1. Ensure vault subfolder exists
    rel_folder = get_folder_for_source(candidate.get("source", ""))
    target_dir = os.path.join(vault_path, rel_folder)
    os.makedirs(target_dir, exist_ok=True)

    # 2. Compute date prefix YYYY-MM-DD
    created_str = candidate.get("created_at", "")
    date_prefix = ""
    if created_str:
        try:
            dt = datetime.strptime(str(created_str)[:10], "%Y-%m-%d")
            date_prefix = dt.strftime("%Y-%m-%d")
        except ValueError:
            date_prefix = datetime.now().strftime("%Y-%m-%d")
    if not date_prefix:
        date_prefix = datetime.now().strftime("%Y-%m-%d")

    # 3. Slugify title and build base filename
    slug = slugify_title(candidate.get("title", ""))
    base_filename = f"{date_prefix}-{slug}.md"
    file_path = os.path.join(target_dir, base_filename)

    # 4. Handle filename collision
    if os.path.exists(file_path):
        counter = 1
        while True:
            candidate_filename = f"{date_prefix}-{slug}-{counter}.md"
            candidate_path = os.path.join(target_dir, candidate_filename)
            if not os.path.exists(candidate_path):
                file_path = candidate_path
                break
            counter += 1

    # 5. Ensure theme note and generate note content
    theme_title = ensure_theme_note_exists(vault_path, candidate.get("category", ""))
    note_content = generate_candidate_note_content(candidate, theme_title)

    # 6. Write file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    logger.info("Successfully wrote candidate note to %s", file_path)
    return file_path


def export_unreviewed_candidates(
    db_path: str = config.DB_PATH,
    vault_path: str = config.OBSIDIAN_VAULT_PATH,
    min_score: float = 0.0,
) -> Dict[str, int]:
    """
    Fetches unreviewed candidates from database and writes them to Obsidian vault.
    Marks candidates reviewed = 1 ONLY IF file write is verified successful.

    :return: Summary statistics dictionary
    """
    init_db(db_path)
    candidates = get_unreviewed_candidates(db_path, min_score=min_score)

    stats = {"found": len(candidates), "exported": 0, "failed": 0}
    logger.info("Found %d unreviewed candidate(s) for export (Min score: %.1f)", len(candidates), min_score)

    for c in candidates:
        cid = c.get("id")
        try:
            file_path = export_candidate_to_vault(c, vault_path)
            # Confirm file write success before updating database
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                if cid is not None:
                    mark_candidate_reviewed(db_path, cid)
                stats["exported"] += 1
            else:
                logger.error("File write verification failed for candidate ID %s", cid)
                stats["failed"] += 1
        except Exception as e:
            logger.error("Failed to export candidate ID %s to Obsidian vault: %s", cid, e, exc_info=True)
            stats["failed"] += 1

    logger.info(
        "Obsidian export complete. Stats: Found=%d | Exported=%d | Failed=%d",
        stats["found"],
        stats["exported"],
        stats["failed"],
    )
    return stats


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    parser = argparse.ArgumentParser(
        description="Export unreviewed research_scanner candidates to an Obsidian vault as Markdown notes."
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Only export candidates with score >= MIN_SCORE (default: 0.0)",
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=config.OBSIDIAN_VAULT_PATH,
        help=f"Path to target Obsidian vault folder (default: {config.OBSIDIAN_VAULT_PATH})",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=config.DB_PATH,
        help=f"Path to SQLite database (default: {config.DB_PATH})",
    )

    args = parser.parse_args()
    export_unreviewed_candidates(db_path=args.db, vault_path=args.vault, min_score=args.min_score)


if __name__ == "__main__":
    main()
