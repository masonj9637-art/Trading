"""
Unit and integration tests for research_scanner.export_to_obsidian module.
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch
import pytest

from research_scanner.db import (
    init_db,
    save_fetched_item,
    save_candidate,
    get_unreviewed_candidates,
    get_fetched_item_by_id,
)
from research_scanner.export_to_obsidian import (
    slugify_title,
    get_folder_for_source,
    format_theme_title,
    ensure_theme_note_exists,
    export_candidate_to_vault,
    export_unreviewed_candidates,
    export_from_curator_decisions,
)


@pytest.fixture
def temp_vault():
    path = tempfile.mkdtemp(prefix="test_vault_")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_slugify_title():
    assert slugify_title("Quantum Error-Correction Breakdown!") == "quantum-error-correction-breakdown"
    assert slugify_title("--- Special: Test #1 ---") == "special-test-1"
    assert slugify_title("") == "untitled"


def test_get_folder_for_source():
    assert get_folder_for_source("arxiv") == os.path.join("raw-signals", "arxiv")
    assert get_folder_for_source("uspto") == os.path.join("raw-signals", "patents")
    assert get_folder_for_source("currents") == os.path.join("raw-signals", "news")
    assert get_folder_for_source("unknown_src") == os.path.join("raw-signals", "other")


def test_format_theme_title():
    assert format_theme_title("quantum computing") == "Quantum Computing"
    assert format_theme_title("ai & machine learning") == "AI & Machine Learning"
    assert format_theme_title("") == "General Technology"


def test_export_candidate_to_vault_creates_markdown(temp_vault):
    candidate = {
        "id": 1,
        "source": "arxiv",
        "external_id": "2401.12345",
        "title": "Quantum Supremacy Demo",
        "url": "http://arxiv.org/abs/2401.12345",
        "summary": "Demonstration of quantum supremacy.",
        "score": 8.5,
        "reason": "Major advancement.",
        "category": "quantum computing",
        "created_at": "2026-07-27 10:00:00",
    }

    file_path = export_candidate_to_vault(candidate, temp_vault, candidate["category"], candidate["reason"])

    assert os.path.exists(file_path)
    assert file_path.startswith(os.path.join(temp_vault, "raw-signals", "arxiv"))
    assert "Quantum Supremacy Demo.md" in file_path

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "---" in content
    assert "status: triaged" in content
    assert "# Quantum Supremacy Demo" in content
    assert "[[Quantum Computing]]" in content
    assert "## Curator Reasoning" in content
    assert "## My Notes" in content

    # Check theme note created
    theme_file = os.path.join(temp_vault, "themes", "Quantum Computing.md")
    assert os.path.exists(theme_file)


def test_export_candidate_to_vault_collision_handling(temp_vault):
    candidate = {
        "id": 1,
        "source": "uspto",
        "external_id": "1800111",
        "title": "Robotic Gripper",
        "url": "https://patentcenter.uspto.gov/applications/1800111",
        "summary": "Robot gripper",
        "score": 7.5,
        "reason": "Good gripper",
        "category": "robotics",
        "created_at": "2026-07-27 10:00:00",
    }

    file_path1 = export_candidate_to_vault(candidate, temp_vault, candidate["category"], candidate["reason"])
    file_path2 = export_candidate_to_vault(candidate, temp_vault, candidate["category"], candidate["reason"])

    assert file_path1 != file_path2
    assert "Robotic Gripper.md" in file_path1
    assert "Robotic Gripper (1).md" in file_path2


def test_export_unreviewed_candidates_transactional_integrity(temp_db, temp_vault):
    c1 = {
        "source": "arxiv",
        "external_id": "2401.0001",
        "title": "Paper One",
        "url": "http://arxiv.org/abs/2401.0001",
        "summary": "Summary 1",
        "score": 9.0,
        "reason": "Reason 1",
        "category": "ai & machine learning",
    }
    c2 = {
        "source": "currents",
        "external_id": "news_002",
        "title": "News Two",
        "url": "http://example.com/news/2",
        "summary": "Summary 2",
        "score": 6.5,
        "reason": "Reason 2",
        "category": "semiconductor",
    }

    save_fetched_item(temp_db, c1)
    save_candidate(temp_db, c1)

    save_fetched_item(temp_db, c2)
    save_candidate(temp_db, c2)

    # 1. Export with min_score = 8.0 -> only c1 exported and marked reviewed
    stats = export_unreviewed_candidates(db_path=temp_db, vault_path=temp_vault, min_score=8.0)
    assert stats["found"] == 1
    assert stats["exported"] == 1

    remaining = get_unreviewed_candidates(temp_db, min_score=0.0)
    assert len(remaining) == 1
    assert remaining[0]["title"] == "News Two"

    # 2. Export with write failure mock -> candidate must NOT be marked reviewed
    with patch("builtins.open", side_effect=IOError("Disk write error")):
        stats_fail = export_unreviewed_candidates(db_path=temp_db, vault_path=temp_vault, min_score=0.0)
        assert stats_fail["failed"] == 1
        assert stats_fail["exported"] == 0

    # Verify candidate c2 remains unreviewed in SQLite
    remaining_after_fail = get_unreviewed_candidates(temp_db, min_score=0.0)
    assert len(remaining_after_fail) == 1
    assert remaining_after_fail[0]["title"] == "News Two"


def test_export_from_curator_decisions_basic(temp_db, temp_vault):
    item = {
        "source": "arxiv",
        "external_id": "2401.9999",
        "title": "Quantum Computing Advances",
        "url": "http://arxiv.org/abs/2401.9999",
        "summary": "Summary of quantum computing advances.",
    }
    save_fetched_item(temp_db, item)
    fetched_item = get_fetched_item_by_id(temp_db, 1)
    assert fetched_item["consumed_by_curator"] == 0

    decisions = [
        {
            "fetched_item_id": 1,
            "category": "quantum computing",
            "reasoning": "Strong evidence of fault tolerance.",
        }
    ]
    decisions_path = os.path.join(temp_vault, "decisions.json")
    with open(decisions_path, "w", encoding="utf-8") as f:
        json.dump(decisions, f)

    stats = export_from_curator_decisions(decisions_path, db_path=temp_db, vault_path=temp_vault)

    assert stats["found"] == 1
    assert stats["exported"] == 1
    assert stats["failed"] == 0

    expected_dir = os.path.join(temp_vault, "raw-signals", "arxiv")
    files = os.listdir(expected_dir)
    assert len(files) == 1
    assert files[0] == "Quantum Computing Advances.md"

    expected_note = os.path.join(expected_dir, files[0])
    with open(expected_note, "r", encoding="utf-8") as f:
        content = f.read()

    assert "[[Quantum Computing]]" in content
    assert "Strong evidence of fault tolerance." in content
    assert "Triage Score" not in content
    assert "Gemma Triage Reason" not in content

    updated_item = get_fetched_item_by_id(temp_db, 1)
    assert updated_item["consumed_by_curator"] == 1


def test_export_from_curator_decisions_escalation_theme(temp_db, temp_vault):
    item = {
        "source": "uspto",
        "external_id": "998877",
        "title": "Superconducting Qubit Architecture",
        "url": "http://uspto.gov/998877",
        "summary": "Patent for qubit architecture.",
    }
    save_fetched_item(temp_db, item)

    decisions = [
        {
            "fetched_item_id": 1,
            "category": "quantum computing",
            "reasoning": "Novel hardware design.",
            "escalation_theme": "Hardware Scaling",
        }
    ]
    decisions_path = os.path.join(temp_vault, "decisions_escalation.json")
    with open(decisions_path, "w", encoding="utf-8") as f:
        json.dump(decisions, f)

    stats = export_from_curator_decisions(decisions_path, db_path=temp_db, vault_path=temp_vault)
    assert stats["exported"] == 1

    expected_dir = os.path.join(temp_vault, "raw-signals", "patents")
    files = os.listdir(expected_dir)
    assert len(files) == 1

    expected_note = os.path.join(expected_dir, files[0])
    with open(expected_note, "r", encoding="utf-8") as f:
        content = f.read()

    assert "[[Quantum Computing]]" in content
    assert "[[Hardware Scaling]]" in content


def test_export_from_curator_decisions_write_failure_integrity(temp_db, temp_vault):
    item = {
        "source": "currents",
        "external_id": "news_123",
        "title": "Market Tech Trends",
        "url": "http://example.com/news/123",
        "summary": "Tech news summary.",
    }
    save_fetched_item(temp_db, item)

    decisions = [
        {
            "fetched_item_id": 1,
            "category": "news",
            "reasoning": "Market update.",
        }
    ]
    decisions_path = os.path.join(temp_vault, "decisions_fail.json")
    with open(decisions_path, "w", encoding="utf-8") as f:
        json.dump(decisions, f)

    orig_open = open

    def mock_open(file, mode="r", *args, **kwargs):
        if "w" in mode:
            raise IOError("Disk write error")
        return orig_open(file, mode, *args, **kwargs)

    with patch("builtins.open", side_effect=mock_open):
        stats = export_from_curator_decisions(decisions_path, db_path=temp_db, vault_path=temp_vault)

    assert stats["found"] == 1
    assert stats["exported"] == 0
    assert stats["failed"] == 1

    updated_item = get_fetched_item_by_id(temp_db, 1)
    assert updated_item["consumed_by_curator"] == 0


def test_export_from_curator_decisions_nonexistent_item_id(temp_db, temp_vault):
    item = {
        "source": "arxiv",
        "external_id": "2401.0001",
        "title": "Existing Item",
        "url": "http://arxiv.org/abs/2401.0001",
        "summary": "Existing item summary.",
    }
    save_fetched_item(temp_db, item)

    decisions = [
        {
            "fetched_item_id": 9999,
            "category": "quantum computing",
            "reasoning": "Non-existent item.",
        },
        {
            "fetched_item_id": 1,
            "category": "quantum computing",
            "reasoning": "Valid item.",
        },
    ]
    decisions_path = os.path.join(temp_vault, "decisions_nonexistent.json")
    with open(decisions_path, "w", encoding="utf-8") as f:
        json.dump(decisions, f)

    stats = export_from_curator_decisions(decisions_path, db_path=temp_db, vault_path=temp_vault)

    assert stats["found"] == 2
    assert stats["exported"] == 1
    assert stats["failed"] == 1

    valid_item = get_fetched_item_by_id(temp_db, 1)
    assert valid_item["consumed_by_curator"] == 1

