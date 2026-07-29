"""
Terminal CLI dashboard for research_scanner.
Lists unreviewed candidate items from SQLite sorted by score.
"""

import argparse
import sys
import logging
from typing import List, Dict, Any

from research_scanner import config
from research_scanner.db import init_db, get_unreviewed_candidates

logger = logging.getLogger("research_scanner.dashboard")


def render_dashboard(db_path: str = config.DB_PATH, min_score: float = 0.0, limit: int = 50) -> None:
    """
    Fetches and displays unreviewed candidates from the database in a terminal-friendly table.
    """
    init_db(db_path)
    candidates = get_unreviewed_candidates(db_path, min_score=min_score)

    if limit and limit > 0:
        candidates = candidates[:limit]

    print("\n" + "=" * 90)
    print(f" RESEARCH SCANNER - UNREVIEWED CANDIDATES (Min Score: {min_score}) ".center(90, "="))
    print("=" * 90)

    if not candidates:
        print("\n No unreviewed candidates found matching criteria.\n")
        print("=" * 90 + "\n")
        return

    # Header
    print(f"{'ID':<5} | {'Score':<6} | {'Source':<8} | {'Category':<22} | {'Title':<40}")
    print("-" * 90)

    category_counts: Dict[str, int] = {}
    for c in candidates:
        cid = str(c.get("id", ""))
        score = f"{c.get('score', 0.0):.1f}"
        source = str(c.get("source", "")).upper()[:8]
        category = str(c.get("category", "uncategorized"))[:22]
        title = str(c.get("title", ""))
        if len(title) > 40:
            title = title[:37] + "..."

        print(f"{cid:<5} | {score:<6} | {source:<8} | {category:<22} | {title:<40}")

        cat_key = c.get("category", "uncategorized").lower()
        category_counts[cat_key] = category_counts.get(cat_key, 0) + 1

    print("-" * 90)
    print(f"Total Listed: {len(candidates)} candidate(s)")
    if category_counts:
        cat_summary = ", ".join([f"{k}: {v}" for k, v in category_counts.items()])
        print(f"Categories: {cat_summary}")
    print("=" * 90 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Terminal CLI dashboard for research_scanner candidates.")
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Filter candidates with score >= MIN_SCORE (default: 0.0)",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=config.DB_PATH,
        help=f"Path to SQLite database (default: {config.DB_PATH})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of candidates to display (default: 50)",
    )

    args = parser.parse_args()
    render_dashboard(db_path=args.db, min_score=args.min_score, limit=args.limit)


if __name__ == "__main__":
    main()
