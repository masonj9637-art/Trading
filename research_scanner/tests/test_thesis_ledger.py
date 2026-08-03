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


def test_parse_fact_check_note_full_frontmatter(temp_vault):
    note_content = """---
ticker: NVDA
audit_date: 2026-07-28
confidence_level: High
fact_check_verdict: claims well-supported
theme_note: Quantum Computing
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
    assert parsed["fact_check_verdict"] == "claims well-supported"
    assert parsed["theme_note"] == "Quantum Computing"


def test_parse_fact_check_note_missing_frontmatter(temp_vault):
    # Missing YAML frontmatter completely; must rely on body regex fallbacks
    note_content = """# Quantum Processing Unit Scaling Audit

- **Ticker**: NVDA
- **Confidence Level**: High

## Independent Fact-Check

Independent audit confirms the primary claims are claims well-supported by sources.

[[Quantum Computing]]
Audit Date: 2026-07-28
"""
    note_path = os.path.join(temp_vault, "2026-07-28-nvda-no-fm.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    parsed = parse_fact_check_note(note_path)
    assert parsed is not None
    assert parsed["ticker"] == "NVDA"
    assert parsed["audit_date"] == "2026-07-28"
    assert parsed["confidence_level"] == "High"
    assert parsed["fact_check_verdict"] == "claims well-supported"
    assert parsed["theme_note"] == "Quantum Computing"


def test_parse_fact_check_note_mismatched_keys_fallback(temp_vault):
    # Frontmatter has mismatched key names (date instead of audit_date, theme instead of theme_note, no confidence field)
    note_content = """---
ticker: NVDA
date: 2026-07-28
theme: Quantum Computing
---

# Quantum Processing Unit Scaling Audit

Confidence Level: Medium

## Independent Fact-Check

Independent analysis indicates some claims overstated by authors.

[[Quantum Computing]]
"""
    note_path = os.path.join(temp_vault, "2026-07-28-nvda-mismatched-keys.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    parsed = parse_fact_check_note(note_path)
    assert parsed is not None
    assert parsed["ticker"] == "NVDA"
    assert parsed["audit_date"] == "2026-07-28"
    assert parsed["confidence_level"] == "Medium"
    assert parsed["fact_check_verdict"] == "some claims overstated"
    assert parsed["theme_note"] == "Quantum Computing"


@pytest.mark.parametrize(
    "confidence_line,expected_level",
    [
        ("Confidence Level: Medium", "Medium"),
        ("Confidence: Low", "Low"),
        ("**Confidence Level**: High", "High"),
        ("**Confidence**: Very High", "Very High"),
    ],
)
def test_parse_fact_check_note_confidence_regex_patterns(temp_vault, confidence_line, expected_level):
    note_content = f"""# Audit Note
{confidence_line}
Ticker: AAPL

## Independent Fact-Check
The claims are well-supported.
2026-07-20
"""
    note_path = os.path.join(temp_vault, "confidence_test.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    parsed = parse_fact_check_note(note_path)
    assert parsed is not None
    assert parsed["confidence_level"] == expected_level


@pytest.mark.parametrize(
    "body_text,expected_verdict",
    [
        ("Independent review shows claims well-supported.", "claims well-supported"),
        ("Independent review shows some claims overstated.", "some claims overstated"),
        ("Independent review shows claims not well-supported by sources.", "claims not well-supported by sources"),
    ],
)
def test_parse_fact_check_note_verdict_phrase_fallbacks(temp_vault, body_text, expected_verdict):
    note_content = f"""# Audit Note
Ticker: MSFT

## Independent Fact-Check
{body_text}
2026-07-20
"""
    note_path = os.path.join(temp_vault, "verdict_test.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    parsed = parse_fact_check_note(note_path)
    assert parsed is not None
    assert parsed["fact_check_verdict"] == expected_verdict


def test_scan_vault_and_update_ledger_immutable(temp_vault, temp_db):
    note_content = """---
ticker: AAPL
audit_date: 2026-07-20
confidence_level: Medium
fact_check_verdict: claims well-supported
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
    assert entries[0]["fact_check_verdict"] == "claims well-supported"

    # Scan 2: Re-scan should detect existing entry and NOT insert duplicate or edit row
    stats2 = scan_vault_and_update_ledger(vault_path=temp_vault, db_path=temp_db)
    assert stats2["added"] == 0
    assert stats2["existing"] == 1

    entries_after = get_all_ledger_entries(temp_db)
    assert len(entries_after) == 1

