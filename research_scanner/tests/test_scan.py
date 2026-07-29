"""
Integration tests for research_scanner.scan entrypoint.
"""

import os
import tempfile
from unittest.mock import patch
import pytest

from research_scanner.scan import run_scan_cycle
from research_scanner.db import get_all_candidates, is_item_fetched, compute_item_hash


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_run_scan_cycle_end_to_end(temp_db_path):
    mock_arxiv_items = [
        {
            "source": "arxiv",
            "external_id": "paper_101",
            "title": "Low Impact Paper",
            "url": "http://arxiv.org/abs/paper_101",
            "summary": "Routine parameter tuning.",
        },
        {
            "source": "arxiv",
            "external_id": "paper_202",
            "title": "High Impact Breakthrough",
            "url": "http://arxiv.org/abs/paper_202",
            "summary": "Foundational milestone in quantum error correction.",
        },
    ]

    def mock_triage(item, host, model):
        if item["external_id"] == "paper_101":
            return {"score": 3.0, "reason": "Incremental", "category": "ai & machine learning"}
        else:
            return {"score": 9.0, "reason": "Breakthrough", "category": "quantum computing"}

    with patch("research_scanner.scan.fetch_arxiv_items", return_value=mock_arxiv_items), \
         patch("research_scanner.scan.fetch_uspto_items", return_value=[]), \
         patch("research_scanner.scan.fetch_currents_items", return_value=[]), \
         patch("research_scanner.scan.triage_item", side_effect=mock_triage), \
         patch("research_scanner.scan.send_discord_notification", return_value=True) as mock_notify:

        # Cycle 1: Process 2 items -> 1 candidate >= threshold 7.0
        stats = run_scan_cycle(db_path=temp_db_path)

        assert stats["fetched"] == 2
        assert stats["new"] == 2
        assert stats["triaged"] == 2
        assert stats["candidates"] == 1
        assert stats["notifications_sent"] == 1

        mock_notify.assert_called_once()
        candidates = get_all_candidates(temp_db_path)
        assert len(candidates) == 1
        assert candidates[0]["title"] == "High Impact Breakthrough"
        assert candidates[0]["score"] == 9.0

        # Cycle 2: Run scan again with same source data (Deduplication test)
        stats2 = run_scan_cycle(db_path=temp_db_path)
        assert stats2["fetched"] == 2
        assert stats2["new"] == 0
        assert stats2["triaged"] == 0
        assert stats2["candidates"] == 0
