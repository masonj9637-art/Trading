"""
Unit tests for research_scanner.log_trade CLI script.
"""

import os
import tempfile
import pytest

from research_scanner.db import init_db, get_all_trades
from research_scanner.log_trade import parse_args, main, build_parser


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_parse_args_valid():
    args = [
        "--ticker", "RGTI",
        "--audit-note", "audits/2026-08-01-rigetti-audit.md",
        "--entry-price", "4.52",
        "--entry-date", "2026-08-08",
        "--notes", "optional free text",
    ]
    parsed = parse_args(args)
    assert parsed.ticker == "RGTI"
    assert parsed.audit_note == "audits/2026-08-01-rigetti-audit.md"
    assert parsed.entry_price == 4.52
    assert parsed.entry_date == "2026-08-08"
    assert parsed.notes == "optional free text"


def test_parse_args_optional_notes_omitted():
    args = [
        "--ticker", "RGTI",
        "--audit-note", "audits/2026-08-01-rigetti-audit.md",
        "--entry-price", "4.52",
        "--entry-date", "2026-08-08",
    ]
    parsed = parse_args(args)
    assert parsed.notes is None


def test_parse_args_missing_required():
    args = ["--ticker", "RGTI"]
    with pytest.raises(SystemExit):
        parse_args(args)


def test_parse_args_invalid_price():
    args = [
        "--ticker", "RGTI",
        "--audit-note", "audits/2026-08-01-rigetti-audit.md",
        "--entry-price", "-1.0",
        "--entry-date", "2026-08-08",
    ]
    with pytest.raises(SystemExit):
        parse_args(args)


def test_parse_args_empty_ticker():
    args = [
        "--ticker", "   ",
        "--audit-note", "audits/2026-08-01-rigetti-audit.md",
        "--entry-price", "4.52",
        "--entry-date", "2026-08-08",
    ]
    with pytest.raises(SystemExit):
        parse_args(args)


def test_main_execution(temp_db, capsys):
    args = [
        "--ticker", "RGTI",
        "--audit-note", "audits/2026-08-01-rigetti-audit.md",
        "--entry-price", "4.52",
        "--entry-date", "2026-08-08",
        "--notes", "Bought 100 shares",
        "--db-path", temp_db,
    ]
    ret = main(args)
    assert ret == 0

    captured = capsys.readouterr()
    assert "Successfully logged trade #1: RGTI @ 4.52 on 2026-08-08" in captured.out
    assert "Notes: Bought 100 shares" in captured.out

    trades = get_all_trades(temp_db)
    assert len(trades) == 1
    assert trades[0]["ticker"] == "RGTI"
    assert trades[0]["entry_price"] == 4.52
    assert trades[0]["notes"] == "Bought 100 shares"
