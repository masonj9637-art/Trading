"""
CLI module for manually logging real trade entries into research_scanner database.

Example:
    python -m research_scanner.log_trade --ticker RGTI \
        --audit-note "audits/2026-08-01-rigetti-audit.md" \
        --entry-price 4.52 \
        --entry-date 2026-08-08 \
        --notes "optional free text"
"""

import argparse
import sys
from typing import List, Optional

from research_scanner.config import DB_PATH
from research_scanner.db import save_trade


def build_parser() -> argparse.ArgumentParser:
    """
    Constructs the command-line argument parser for logging trades.
    """
    parser = argparse.ArgumentParser(
        description="Log a real trade entry into the database."
    )
    parser.add_argument(
        "--ticker",
        required=True,
        help="Ticker symbol (e.g. RGTI)",
    )
    parser.add_argument(
        "--audit-note",
        required=True,
        help="Path to Analyst/Skeptic-reviewed thesis audit note markdown file",
    )
    parser.add_argument(
        "--entry-price",
        type=float,
        required=True,
        help="Execution entry price (e.g. 4.52)",
    )
    parser.add_argument(
        "--entry-date",
        required=True,
        help="Entry date (e.g. 2026-08-08)",
    )
    parser.add_argument(
        "--notes",
        default=None,
        help="Optional free text notes",
    )
    parser.add_argument(
        "--db-path",
        default=DB_PATH,
        help=f"Path to SQLite database (default: {DB_PATH})",
    )
    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses and validates CLI arguments.
    """
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.ticker.strip():
        parser.error("--ticker cannot be empty.")
    if not parsed_args.audit_note.strip():
        parser.error("--audit-note cannot be empty.")
    if parsed_args.entry_price <= 0:
        parser.error("--entry-price must be greater than 0.")
    if not parsed_args.entry_date.strip():
        parser.error("--entry-date cannot be empty.")

    return parsed_args


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for logging a trade.
    """
    parsed_args = parse_args(args)

    trade = {
        "ticker": parsed_args.ticker,
        "audit_note_path": parsed_args.audit_note,
        "entry_price": parsed_args.entry_price,
        "entry_date": parsed_args.entry_date,
        "notes": parsed_args.notes,
    }

    trade_id = save_trade(parsed_args.db_path, trade)
    print(
        f"Successfully logged trade #{trade_id}: {parsed_args.ticker.upper()} "
        f"@ {parsed_args.entry_price:.2f} on {parsed_args.entry_date} "
        f"(Audit note: {parsed_args.audit_note})"
    )
    if parsed_args.notes:
        print(f"Notes: {parsed_args.notes}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
