"""
Unit and integration tests for research_scanner.scoring module.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from research_scanner.db import (
    init_db,
    save_thesis_ledger_entry,
    get_all_thesis_scores,
)
from research_scanner.scoring import (
    calculate_cost_adjusted_return,
    is_horizon_eligible,
    score_unscored_theses,
    generate_scoring_report,
    get_baseline_ticker,
    BASELINE_TICKER_POOL,
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_calculate_cost_adjusted_return():
    # 100 to 110 (+10% gross return)
    # net_return = (110 / 100) * (1.0 - 0.0010) - 1.0 = 1.10 * 0.999 - 1.0 = 0.0989 (+9.89%)
    net_ret = calculate_cost_adjusted_return(100.0, 110.0, bps=10.0)
    assert abs(net_ret - 0.0989) < 0.0001
    assert net_ret < 0.10  # Cost-adjusted return is strictly less than 10% gross


def test_is_horizon_eligible():
    # Old audit date (100 calendar days ago) is eligible for 20D and 60D
    assert is_horizon_eligible("2026-01-01", 20) is True
    assert is_horizon_eligible("2026-01-01", 60) is True

    # Future/recent audit date (today) is NOT eligible for 20D horizon
    today_str = "2026-07-28"
    assert is_horizon_eligible(today_str, 20) is False


def test_score_unscored_theses_success(temp_db):
    entry = {
        "ledger_hash": "hash_123",
        "ticker": "NVDA",
        "audit_date": "2026-01-01",
        "confidence_level": "High",
        "fact_check_verdict": "Supported",
        "theme_note": "quantum computing",
        "vault_note_path": "/path/to/note.md",
    }
    save_thesis_ledger_entry(temp_db, entry)

    with patch("research_scanner.scoring.send_discord_notification", return_value=True) as mock_notify:
        stats = score_unscored_theses(db_path=temp_db, mock=True)

    assert stats["scored"] > 0
    assert stats["notifications_sent"] > 0
    mock_notify.assert_called()

    scores = get_all_thesis_scores(temp_db)
    assert len(scores) > 0
    assert scores[0]["ticker"] == "NVDA"
    assert "net_return" in scores[0]
    assert "baseline_net_return" in scores[0]


def test_generate_scoring_report_underpowered(temp_db, capsys):
    entry = {
        "ledger_hash": "hash_456",
        "ticker": "MSFT",
        "audit_date": "2026-01-01",
        "confidence_level": "Medium",
        "fact_check_verdict": "Supported",
        "theme_note": "ai & machine learning",
        "vault_note_path": "/path/to/note2.md",
    }
    save_thesis_ledger_entry(temp_db, entry)

    # Score entry
    with patch("research_scanner.scoring.send_discord_notification", return_value=True):
        score_unscored_theses(db_path=temp_db, mock=True)

    # Generate report with min_n = 30 floor
    generate_scoring_report(db_path=temp_db, min_n=30)

    captured = capsys.readouterr()
    assert "FORWARD THESIS SCORING REPORT" in captured.out
    assert "UNDERPOWERED STATUS" in captured.out
    assert "Refusing to state a directional conclusion" in captured.out


def test_score_unscored_theses_baseline_price_failure_skip(temp_db, caplog):
    entry = {
        "ledger_hash": "hash_baseline_fail",
        "ticker": "AAPL",
        "audit_date": "2026-01-01",
        "confidence_level": "High",
        "fact_check_verdict": "Supported",
        "theme_note": "tech",
        "vault_note_path": "/path/to/note.md",
    }
    save_thesis_ledger_entry(temp_db, entry)

    # Mock get_alpaca_price so thesis prices succeed but baseline exit price fails (returns None)
    def mock_get_price(ticker, target_date, **kwargs):
        if ticker == "AAPL":
            return 150.0
        # For baseline ticker, return price on entry date, but None on exit date
        if target_date == "2026-01-01":
            return 100.0
        return None

    with patch("research_scanner.scoring.get_alpaca_price", side_effect=mock_get_price):
        stats = score_unscored_theses(db_path=temp_db, mock=False)

    # Verify thesis entry was skipped (not scored, no db row written)
    assert stats["scored"] == 0
    scores = get_all_thesis_scores(temp_db)
    assert len(scores) == 0

    # Verify warning log message
    assert "Could not fetch valid baseline price" in caplog.text


def test_get_baseline_ticker_consumed_filter(temp_db):
    from research_scanner.db import get_db_connection
    # Insert items into fetched_items:
    # 1. Item with consumed_by_curator = 0 containing $TSLA
    # 2. Item with consumed_by_curator = 1 containing $AMD
    conn = get_db_connection(temp_db)
    with conn:
        conn.execute(
            "INSERT INTO fetched_items (item_hash, source, external_id, title, summary, consumed_by_curator, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("hash_unpromoted", "test", "1", "Analysis of $TSLA EV growth", "TSLA looks interesting", 0, "2026-01-01 10:00:00")
        )
        conn.execute(
            "INSERT INTO fetched_items (item_hash, source, external_id, title, summary, consumed_by_curator, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("hash_promoted", "test", "2", "Analysis of $AMD chips", "AMD looks strong", 1, "2026-01-01 10:00:00")
        )
    conn.close()

    # get_baseline_ticker should pick TSLA (consumed_by_curator = 0) and not AMD (consumed_by_curator = 1)
    ticker = get_baseline_ticker(temp_db, "2026-01-01", thesis_ticker="NVDA")
    assert ticker == "TSLA"


def test_get_baseline_ticker_fallback(temp_db):
    # When no unconsumed fetched_items exist in +/- 14 day window
    ticker = get_baseline_ticker(temp_db, "2026-01-01", thesis_ticker="SPY")
    assert ticker in BASELINE_TICKER_POOL
    assert ticker != "SPY"

