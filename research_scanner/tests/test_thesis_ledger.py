"""
Unit and integration tests for research_scanner.thesis_ledger module.
"""

import os
import shutil
import tempfile
import pytest

from research_scanner.db import init_db, get_all_ledger_entries
from research_scanner.thesis_ledger import (
    compute_ledger_hash,
    parse_fact_check_note,
    scan_vault_and_update_ledger,
)


@pytest.fixture
def temp_vault():
    path = tempfile.mkdtemp(prefix="test_ledger_vault_")
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


def test_compute_ledger_hash():
    h1 = compute_ledger_hash("/path/to/note1.md")
    h2 = compute_ledger_hash(" /path/to/note1.md ")
    assert h1 == h2
    assert len(h1) == 64


def test_parse_fact_check_note(temp_vault):
    note_content = """---
ticker: NVDA
audit_date: 2026-07-28
confidence_level: High
fact_check_verdict: Supported
category: quantum computing
---

# Quantum Processing Unit Scaling Audit

- **Source**: ARXIV

## Independent Fact-Check

Independent audit confirms GPU architecture claims are backed by physical benchmarks.

## My Notes
"""
    note_path = os.path.join(temp_vault, "2026-07-28-nvda-quantum-audit.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    parsed = parse_fact_check_note(note_path)
    assert parsed is not None
    assert parsed["ticker"] == "NVDA"
    assert parsed["audit_date"] == "2026-07-28"
    assert parsed["confidence_level"] == "High"
    assert parsed["fact_check_verdict"] == "Supported"
    assert parsed["theme_note"] == "quantum computing"


def test_parse_fact_check_note_incomplete(temp_vault):
    # Note without ## Independent Fact-Check section
    note_content = """# Regular Note without fact-check section\n\nNo evaluation here."""
    note_path = os.path.join(temp_vault, "regular_note.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    parsed = parse_fact_check_note(note_path)
    assert parsed is None


def test_scan_vault_and_update_ledger_immutable(temp_vault, temp_db):
    note_content = """---
ticker: AAPL
audit_date: 2026-07-20
confidence_level: Medium
fact_check_verdict: Inconclusive
---
# Test Audit Note
## Independent Fact-Check
Details of independent verification.
"""
    note_path = os.path.join(temp_vault, "2026-07-20-aapl-audit.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    # Scan 1: New entry added
    stats1 = scan_vault_and_update_ledger(vault_path=temp_vault, db_path=temp_db)
    assert stats1["added"] == 1
    assert stats1["existing"] == 0

    entries = get_all_ledger_entries(temp_db)
    assert len(entries) == 1
    assert entries[0]["ticker"] == "AAPL"
    assert entries[0]["fact_check_verdict"] == "Inconclusive"

    # Scan 2: Re-scan should detect existing entry and NOT insert duplicate or edit row
    stats2 = scan_vault_and_update_ledger(vault_path=temp_vault, db_path=temp_db)
    assert stats2["added"] == 0
    assert stats2["existing"] == 1

    entries_after = get_all_ledger_entries(temp_db)
    assert len(entries_after) == 1
