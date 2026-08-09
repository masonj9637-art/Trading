"""
Unit tests for heartbeat_check.py and run_daemon last_success timestamp updates.
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest

from research_scanner.heartbeat_check import (
    check_heartbeat,
    parse_iso_timestamp,
    get_timestamp_age_seconds,
)
from research_scanner.run_daemon import update_last_success


def test_parse_iso_timestamp():
    dt1 = parse_iso_timestamp("2026-08-09T10:00:00")
    assert dt1 is not None
    assert dt1.year == 2026

    dt2 = parse_iso_timestamp("2026-08-09T10:00:00Z")
    assert dt2 is not None
    assert dt2.tzinfo == timezone.utc

    assert parse_iso_timestamp(None) is None
    assert parse_iso_timestamp("invalid-date") is None


def test_fresh_timestamps_produce_no_alert(tmp_path):
    now = datetime(2026, 8, 9, 12, 0, 0)
    # scan_and_curator 1h old (threshold 6h), director 2h old (threshold 8h)
    data = {
        "scan_and_curator": (now - timedelta(hours=1)).isoformat(),
        "director": (now - timedelta(hours=2)).isoformat(),
    }
    json_path = tmp_path / "last_success.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with patch("research_scanner.notifier.send_discord_message") as mock_send:
        res = check_heartbeat(filepath=str(json_path), now=now, send_discord=True)

        assert res["healthy"] is True
        assert len(res["stale_components"]) == 0
        assert mock_send.call_count == 0


def test_stale_timestamp_produces_exactly_one_correctly_worded_alert(tmp_path):
    now = datetime(2026, 8, 9, 12, 0, 0)
    # scan_and_curator 7h old (stale, threshold 6h), director 2h old (healthy)
    data = {
        "scan_and_curator": (now - timedelta(hours=7)).isoformat(),
        "director": (now - timedelta(hours=2)).isoformat(),
    }
    json_path = tmp_path / "last_success.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with patch("research_scanner.notifier.send_discord_message", return_value=True) as mock_send:
        res = check_heartbeat(filepath=str(json_path), now=now, send_discord=True)

        assert res["healthy"] is False
        assert res["stale_components"] == ["scan_and_curator"]
        assert mock_send.call_count == 1

        content = mock_send.call_args[1].get("content") or mock_send.call_args[0][0]
        assert "scan_and_curator" in content
        assert "gone silent" in content
        assert "7.0 hours" in content


def test_stale_director_timestamp_produces_alert(tmp_path):
    now = datetime(2026, 8, 9, 12, 0, 0)
    # scan_and_curator 1h old (healthy), director 9h old (stale, threshold 8h)
    data = {
        "scan_and_curator": (now - timedelta(hours=1)).isoformat(),
        "director": (now - timedelta(hours=9)).isoformat(),
    }
    json_path = tmp_path / "last_success.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with patch("research_scanner.notifier.send_discord_message", return_value=True) as mock_send:
        res = check_heartbeat(filepath=str(json_path), now=now, send_discord=True)

        assert res["healthy"] is False
        assert res["stale_components"] == ["director"]
        assert mock_send.call_count == 1

        content = mock_send.call_args[1].get("content") or mock_send.call_args[0][0]
        assert "director" in content
        assert "gone silent" in content
        assert "9.0 hours" in content


def test_missing_file_treated_as_stale_no_crash(tmp_path):
    json_path = tmp_path / "non_existent_file.json"

    with patch("research_scanner.notifier.send_discord_message", return_value=True) as mock_send:
        res = check_heartbeat(filepath=str(json_path), send_discord=True)

        assert res["healthy"] is False
        assert "scan_and_curator" in res["stale_components"]
        assert "director" in res["stale_components"]
        assert mock_send.call_count == 1

        content = mock_send.call_args[1].get("content") or mock_send.call_args[0][0]
        assert "scan_and_curator" in content
        assert "director" in content
        assert "missing timestamp" in content


def test_missing_key_treated_as_stale(tmp_path):
    now = datetime(2026, 8, 9, 12, 0, 0)
    # Only director timestamp present
    data = {
        "director": (now - timedelta(hours=1)).isoformat(),
    }
    json_path = tmp_path / "last_success.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    with patch("research_scanner.notifier.send_discord_message", return_value=True) as mock_send:
        res = check_heartbeat(filepath=str(json_path), now=now, send_discord=True)

        assert res["healthy"] is False
        assert res["stale_components"] == ["scan_and_curator"]
        assert mock_send.call_count == 1


def test_update_last_success_preserves_existing_keys(tmp_path):
    json_path = tmp_path / "last_success.json"
    initial_data = {
        "director": "2026-08-09T08:00:00",
        "custom_key": "some_value",
    }
    json_path.write_text(json.dumps(initial_data), encoding="utf-8")

    ts = update_last_success(key="scan_and_curator", filepath=str(json_path), timestamp="2026-08-09T10:00:00")

    updated_data = json.loads(json_path.read_text(encoding="utf-8"))
    assert updated_data["director"] == "2026-08-09T08:00:00"
    assert updated_data["custom_key"] == "some_value"
    assert updated_data["scan_and_curator"] == "2026-08-09T10:00:00"
