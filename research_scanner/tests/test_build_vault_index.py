"""
Unit tests for build_vault_index.py module.
"""

import os
import logging
import pytest
from research_scanner.build_vault_index import (
    build_vault_index,
    parse_note,
    parse_yaml_frontmatter,
    extract_gist,
    extract_h1_title,
    extract_first_sentence,
)


def test_mixed_vault_grouped_output(tmp_path):
    """
    Tests that a vault with a mix of raw-signals, themes, and audit notes
    (including audit notes with/without completed fact-check) produces correct grouped output.
    """
    vault_dir = tmp_path / "obsidian_vault"
    raw_dir = vault_dir / "raw-signals" / "arxiv"
    themes_dir = vault_dir / "themes"
    audits_dir = vault_dir / "audits"

    raw_dir.mkdir(parents=True)
    themes_dir.mkdir(parents=True)
    audits_dir.mkdir(parents=True)

    # 1. Raw signals note
    raw_note = raw_dir / "2026-08-01-quantum-sim.md"
    raw_note.write_text(
        "---\n"
        "source: arxiv\n"
        "category: quantum computing\n"
        "fetched_at: 2026-08-01 10:00:00\n"
        "status: triaged\n"
        "---\n\n"
        "# Quantum Simulation Breakthrough\n\n"
        "## Curator Reasoning\n"
        "Demonstrates scalable error mitigation for noisy intermediate-scale quantum devices.\n\n"
        "## Summary / Abstract\n"
        "Abstract content here.\n",
        encoding="utf-8",
    )

    # 2. Theme note
    theme_note = themes_dir / "Quantum Computing.md"
    theme_note.write_text(
        "---\n"
        "category: Quantum Computing\n"
        "status: active\n"
        "created_at: 2026-08-01\n"
        "---\n\n"
        "# Quantum Computing\n\n"
        "Automated theme note collecting research papers, patents, and news signals.\n",
        encoding="utf-8",
    )

    # 3. Audit note without completed fact-check
    audit_pending = audits_dir / "2026-08-01-rigetti-audit.md"
    audit_pending.write_text(
        "---\n"
        "ticker: RGTI\n"
        "audit_date: 2026-08-01\n"
        "confidence_level: medium\n"
        "theme_note: Quantum Computing\n"
        "status: in_review\n"
        "---\n\n"
        "# Rigetti Computing Audit\n\n"
        "1. Thesis Summary\n"
        "Rigetti is transitioning to modular multi-chip architectures for quantum processors.\n\n"
        "2. Supporting Evidence\n"
        "- Multi-chip patent filed in 2025.\n",
        encoding="utf-8",
    )

    # 4. Audit note with completed fact-check
    audit_completed = audits_dir / "2026-08-01-ibm-audit.md"
    audit_completed.write_text(
        "---\n"
        "ticker: IBM\n"
        "audit_date: 2026-08-01\n"
        "confidence_level: high\n"
        "theme_note: Quantum Computing\n"
        "status: completed\n"
        "fact_check_verdict: claims well-supported\n"
        "---\n\n"
        "# IBM Quantum Advantage Audit\n\n"
        "1. Thesis Summary\n"
        "IBM Eagle processor shows verifiable utility-scale simulation advantages.\n\n"
        "## Independent Fact-Check\n"
        "All claims verified against Nature peer-reviewed paper.\n\n"
        "Verdict: claims well-supported\n",
        encoding="utf-8",
    )

    index_file = build_vault_index(str(vault_dir))
    assert os.path.exists(index_file)

    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify header sections
    assert "# Vault Index" in content
    assert "## Raw Signals" in content
    assert "## Themes" in content
    assert "## Audits" in content

    # Verify raw signals entry
    assert "raw-signals/arxiv/2026-08-01-quantum-sim.md" in content
    assert "Title: Quantum Simulation Breakthrough" in content
    assert "Category: quantum computing" in content
    assert "Status: triaged" in content
    assert "Date: 2026-08-01" in content
    assert "Gist: Demonstrates scalable error mitigation for noisy intermediate-scale quantum devices." in content

    # Verify theme entry
    assert "themes/Quantum Computing.md" in content
    assert "Title: Quantum Computing" in content
    assert "Gist: Automated theme note collecting research papers, patents, and news signals." in content

    # Verify audit note without fact-check
    assert "audits/2026-08-01-rigetti-audit.md" in content
    assert "Title: Rigetti Computing Audit" in content
    assert "Status: in_review" in content
    assert "Gist: Rigetti is transitioning to modular multi-chip architectures for quantum processors." in content

    # Verify audit note with completed fact-check contains confidence and verdict
    assert "audits/2026-08-01-ibm-audit.md" in content
    assert "Title: IBM Quantum Advantage Audit" in content
    assert "Confidence: high" in content
    assert "Verdict: claims well-supported" in content
    assert "Gist: IBM Eagle processor shows verifiable utility-scale simulation advantages." in content


def test_malformed_frontmatter_note_skipped(tmp_path, caplog):
    """
    Tests that a note with malformed/missing frontmatter is skipped with a logged warning
    rather than crashing the whole index build.
    """
    vault_dir = tmp_path / "obsidian_vault"
    raw_dir = vault_dir / "raw-signals" / "news"
    raw_dir.mkdir(parents=True)

    # Valid note
    valid_note = raw_dir / "valid.md"
    valid_note.write_text(
        "---\n"
        "source: news\n"
        "category: AI\n"
        "fetched_at: 2026-08-02\n"
        "status: triaged\n"
        "---\n\n"
        "# Valid AI News Note\n\n"
        "## Curator Reasoning\n"
        "Important news regarding AI hardware accelerators.\n",
        encoding="utf-8",
    )

    # Note missing frontmatter
    no_fm_note = raw_dir / "no_frontmatter.md"
    no_fm_note.write_text(
        "# Just Header No Frontmatter\n\nSome text content.",
        encoding="utf-8",
    )

    # Note with malformed frontmatter (syntax error/no colon)
    malformed_note = raw_dir / "malformed.md"
    malformed_note.write_text(
        "---\n"
        "this is invalid yaml key value format without colons\n"
        "---\n\n"
        "# Bad Note\n",
        encoding="utf-8",
    )

    with caplog.at_level(logging.WARNING):
        index_file = build_vault_index(str(vault_dir))

    assert os.path.exists(index_file)

    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Valid note should be included
    assert "valid.md" in content
    assert "Title: Valid AI News Note" in content

    # Invalid notes must be excluded
    assert "no_frontmatter.md" not in content
    assert "malformed.md" not in content

    # Warnings should be logged
    warning_logs = [record.message for record in caplog.records if record.levelno == logging.WARNING]
    assert len(warning_logs) >= 2
    assert any("no_frontmatter.md" in msg for msg in warning_logs)
    assert any("malformed.md" in msg for msg in warning_logs)


def test_empty_vault_index(tmp_path):
    """
    Tests that an empty vault produces a valid (near-empty) index file rather than erroring.
    """
    vault_dir = tmp_path / "empty_vault"
    vault_dir.mkdir(parents=True)

    index_file = build_vault_index(str(vault_dir))
    assert os.path.exists(index_file)

    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# Vault Index" in content
    assert "## Raw Signals" in content
    assert "## Themes" in content
    assert "## Audits" in content
