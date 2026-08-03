"""
Integration tests for research_scanner.scan entrypoint.
"""

import os
import tempfile
from unittest.mock import patch
import pytest

from research_scanner.scan import run_scan_cycle

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

    with patch("research_scanner.scan.fetch_arxiv_items", return_value=mock_arxiv_items), \
         patch("research_scanner.scan.fetch_uspto_items", return_value=[]), \
         patch("research_scanner.scan.fetch_currents_items", return_value=[]), \
         patch("research_scanner.scan.fetch_openalex_items", return_value=[]):

        # Cycle 1: Process 2 items
        stats = run_scan_cycle(db_path=temp_db_path)

        assert stats["fetched"] == 2
        assert stats["new"] == 2

        # Cycle 2: Run scan again with same source data (Deduplication test)
        stats2 = run_scan_cycle(db_path=temp_db_path)
        assert stats2["fetched"] == 2
        assert stats2["new"] == 0
