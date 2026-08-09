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
    get_fetched_item_by_id,
    get_unconsumed_items,
    mark_item_consumed,
    mark_items_reviewed,
    save_trade,
    get_all_trades,
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


def test_mark_item_consumed_promoted(temp_db):
    item = {
        "source": "arxiv",
        "external_id": "2401.99999",
        "title": "Promoted Quantum Paper",
        "url": "http://arxiv.org/abs/2401.99999",
        "summary": "Quantum paper.",
    }
    save_fetched_item(temp_db, item)
    unconsumed = get_unconsumed_items(temp_db)
    item_id = unconsumed[0]["id"]

    success = mark_item_consumed(temp_db, item_id)
    assert success is True

    fetched = get_fetched_item_by_id(temp_db, item_id)
    assert fetched["consumed_by_curator"] == 1
    assert fetched["curator_decision"] == "promoted"


def test_mark_items_reviewed_not_promoted(temp_db):
    item1 = {
        "source": "arxiv",
        "external_id": "2401.11111",
        "title": "Rejected Paper 1",
        "url": "http://arxiv.org/abs/2401.11111",
        "summary": "Summary 1",
    }
    item2 = {
        "source": "arxiv",
        "external_id": "2401.22222",
        "title": "Rejected Paper 2",
        "url": "http://arxiv.org/abs/2401.22222",
        "summary": "Summary 2",
    }
    save_fetched_item(temp_db, item1)
    save_fetched_item(temp_db, item2)

    unconsumed = get_unconsumed_items(temp_db)
    ids = [i["id"] for i in unconsumed]
    assert len(ids) == 2

    count = mark_items_reviewed(temp_db, ids)
    assert count == 2

    for i_id in ids:
        fetched = get_fetched_item_by_id(temp_db, i_id)
        assert fetched["consumed_by_curator"] == 1
        assert fetched["curator_decision"] == "reviewed_not_promoted"

    assert len(get_unconsumed_items(temp_db)) == 0


def test_unconsumed_item_remains_unconsumed(temp_db):
    item = {
        "source": "arxiv",
        "external_id": "2401.33333",
        "title": "Unsent Paper",
        "url": "http://arxiv.org/abs/2401.33333",
        "summary": "Summary 3",
    }
    save_fetched_item(temp_db, item)

    unconsumed = get_unconsumed_items(temp_db)
    assert len(unconsumed) == 1
    item_id = unconsumed[0]["id"]
    fetched = get_fetched_item_by_id(temp_db, item_id)
    assert fetched["consumed_by_curator"] == 0 or fetched["consumed_by_curator"] is None
    assert fetched["curator_decision"] is None


def test_save_trade_and_get_all_trades(temp_db):
    trade1 = {
        "ticker": "rgti",
        "audit_note_path": "audits/2026-08-01-rigetti-audit.md",
        "entry_price": 4.52,
        "entry_date": "2026-08-08",
        "notes": "initial position",
    }
    trade2 = {
        "ticker": "ionq",
        "audit_note_path": "audits/2026-08-02-ionq-audit.md",
        "entry_price": 12.10,
        "entry_date": "2026-08-09",
        "notes": None,
    }

    id1 = save_trade(temp_db, trade1)
    id2 = save_trade(temp_db, trade2)

    assert id1 > 0
    assert id2 > id1

    trades = get_all_trades(temp_db)
    assert len(trades) == 2
    # Order should be id DESC (latest first)
    assert trades[0]["id"] == id2
    assert trades[0]["ticker"] == "IONQ"
    assert trades[0]["entry_price"] == 12.10
    assert trades[0]["notes"] is None
    assert trades[0]["logged_at"] is not None

    assert trades[1]["id"] == id1
    assert trades[1]["ticker"] == "RGTI"
    assert trades[1]["audit_note_path"] == "audits/2026-08-01-rigetti-audit.md"
    assert trades[1]["entry_price"] == 4.52
    assert trades[1]["entry_date"] == "2026-08-08"
    assert trades[1]["notes"] == "initial position"

