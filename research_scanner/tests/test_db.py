"""
Unit tests for research_scanner.db module.
"""

import os
import tempfile
import pytest

from research_scanner.db import (
    init_db,
    compute_item_hash,
    is_item_fetched,
    save_fetched_item,
    save_candidate,
    get_all_candidates,
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_compute_item_hash():
    hash1 = compute_item_hash("arxiv", "2401.12345")
    hash2 = compute_item_hash("ARXIV", "2401.12345 ")
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 length


def test_save_and_check_fetched_item(temp_db):
    item = {
        "source": "arxiv",
        "external_id": "2401.12345",
        "title": "Quantum Supremacy Demo",
        "url": "http://arxiv.org/abs/2401.12345",
        "summary": "Demonstration of quantum supremacy.",
    }
    item_hash = compute_item_hash(item["source"], item["external_id"])

    assert not is_item_fetched(temp_db, item_hash)

    saved = save_fetched_item(temp_db, item)
    assert saved is True
    assert is_item_fetched(temp_db, item_hash) is True

    # Duplicate insert should return False
    saved_again = save_fetched_item(temp_db, item)
    assert saved_again is False


def test_save_and_retrieve_candidate(temp_db):
    candidate = {
        "source": "uspto",
        "external_id": "18/123456",
        "title": "Novel Superconducting Qubit",
        "url": "https://patentcenter.uspto.gov/applications/18123456",
        "summary": "Patent abstract for qubit layout.",
        "score": 8.5,
        "reason": "Significant hardware advancement.",
        "category": "quantum computing",
    }

    # Must save to fetched_items first or insert directly
    item_hash = compute_item_hash(candidate["source"], candidate["external_id"])
    candidate["item_hash"] = item_hash
    save_fetched_item(temp_db, candidate)

    saved = save_candidate(temp_db, candidate)
    assert saved is True

    candidates = get_all_candidates(temp_db)
    assert len(candidates) == 1
    assert candidates[0]["title"] == "Novel Superconducting Qubit"
    assert candidates[0]["score"] == 8.5
    assert candidates[0]["category"] == "quantum computing"
