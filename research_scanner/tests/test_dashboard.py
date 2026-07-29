"""
Unit tests for research_scanner.dashboard module.
"""

import os
import tempfile
import pytest

from research_scanner.db import init_db, save_fetched_item, save_candidate
from research_scanner.dashboard import render_dashboard


@pytest.fixture
def temp_db_with_candidates():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)

    c1 = {
        "source": "arxiv",
        "external_id": "item1",
        "title": "Quantum Supremacy Breakthrough",
        "url": "http://arxiv.org/abs/item1",
        "summary": "Quantum experiment",
        "score": 9.2,
        "reason": "Major milestone",
        "category": "quantum computing",
    }
    c2 = {
        "source": "uspto",
        "external_id": "item2",
        "title": "Autonomous Bipedal Robot",
        "url": "http://patentcenter.uspto.gov/app/item2",
        "summary": "Robot patent",
        "score": 8.0,
        "reason": "Good design",
        "category": "robotics",
    }

    save_fetched_item(path, c1)
    save_candidate(path, c1)

    save_fetched_item(path, c2)
    save_candidate(path, c2)

    yield path

    if os.path.exists(path):
        os.remove(path)


def test_render_dashboard_stdout(temp_db_with_candidates, capsys):
    render_dashboard(db_path=temp_db_with_candidates, min_score=0.0)

    captured = capsys.readouterr()
    assert "UNREVIEWED CANDIDATES" in captured.out
    assert "Quantum Supremacy Breakthrough" in captured.out
    assert "Autonomous Bipedal Robot" in captured.out
    assert "Total Listed: 2" in captured.out


def test_render_dashboard_min_score_filter(temp_db_with_candidates, capsys):
    render_dashboard(db_path=temp_db_with_candidates, min_score=9.0)

    captured = capsys.readouterr()
    assert "Quantum Supremacy Breakthrough" in captured.out
    assert "Autonomous Bipedal Robot" not in captured.out
    assert "Total Listed: 1" in captured.out
