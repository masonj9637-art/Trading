"""
Unit tests for director_run.py module.
"""

import json
import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from research_scanner import director_run
from research_scanner.director_run import (
    get_director_prompt,
    run_director_step,
    update_last_success_timestamp,
    validate_director_output,
)


def test_get_director_prompt_reads_vault_and_context(tmp_path):
    """Verify get_director_prompt reads and embeds vault index, priorities, and context files."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    (vault_dir / "vault-index.md").write_text("# Vault Index Summary", encoding="utf-8")
    (vault_dir / "current-priorities.md").write_text("1. Quantum Computing Priorities", encoding="utf-8")

    context_dir = tmp_path / "context"
    context_dir.mkdir()
    (context_dir / "user_notes.txt").write_text("User preference: focus on quantum hardware", encoding="utf-8")
    (context_dir / "alpha_strategy.md").write_text("Strategy details: low latency", encoding="utf-8")

    prompt = get_director_prompt(vault_path=str(vault_dir), context_path=str(context_dir))

    assert "Vault Index Summary" in prompt
    assert "Quantum Computing Priorities" in prompt
    assert "user_notes.txt" in prompt
    assert "User preference: focus on quantum hardware" in prompt
    assert "alpha_strategy.md" in prompt
    assert "Strategy details: low latency" in prompt


def test_get_director_prompt_empty_context_folder(tmp_path):
    """Verify empty context folder does not crash prompt generation."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    (vault_dir / "vault-index.md").write_text("# Empty Vault Index", encoding="utf-8")
    (vault_dir / "current-priorities.md").write_text("Priority 1", encoding="utf-8")

    context_dir = tmp_path / "empty_context"
    context_dir.mkdir()

    prompt = get_director_prompt(vault_path=str(vault_dir), context_path=str(context_dir))

    assert "Empty Vault Index" in prompt
    assert "Priority 1" in prompt
    assert "(No context files present)" in prompt


def test_validate_director_output():
    """Verify validate_director_output schema checks."""
    valid_data = {
        "updated_priorities": "New Priorities",
        "fetch_requests": [{"query": "arxiv search", "source_hint": "arxiv"}],
        "escalation": {"theme": "Theme A", "message": "High importance"},
        "proactive_message": "Status update message",
    }
    assert validate_director_output(valid_data) is True

    # Empty dict is valid (all keys optional)
    assert validate_director_output({}) is True

    # Root not a dict
    assert validate_director_output(["invalid", "list"]) is False

    # Key type mismatches
    assert validate_director_output({"updated_priorities": 123}) is False
    assert validate_director_output({"fetch_requests": "not a list"}) is False
    assert validate_director_output({"escalation": ["not", "a", "dict"]}) is False
    assert validate_director_output({"proactive_message": 456}) is False


def test_update_last_success_timestamp_creates_and_preserves(tmp_path):
    """Verify update_last_success_timestamp creates file and preserves existing keys."""
    ts_file = tmp_path / "last_success.json"
    ts_file.write_text(json.dumps({"curator": "2026-08-08T12:00:00+00:00"}), encoding="utf-8")

    update_last_success_timestamp(timestamp_path=str(ts_file), key="director")

    assert ts_file.exists()
    content = json.loads(ts_file.read_text(encoding="utf-8"))
    assert "curator" in content
    assert content["curator"] == "2026-08-08T12:00:00+00:00"
    assert "director" in content
    assert len(content["director"]) > 0


@patch("research_scanner.director_run.subprocess.run")
def test_run_director_step_success(mock_subproc_run, tmp_path):
    """Verify successful Director step run produces output JSON, updates vault, and updates timestamp."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    (vault_dir / "vault-index.md").write_text("# Index", encoding="utf-8")
    (vault_dir / "current-priorities.md").write_text("Old Priorities", encoding="utf-8")

    context_dir = tmp_path / "context"
    context_dir.mkdir()

    output_path = tmp_path / "director_output.json"
    timestamp_path = tmp_path / "last_success.json"
    timestamp_path.write_text(json.dumps({"curator": "2026-08-08T10:00:00"}), encoding="utf-8")

    db_path = str(tmp_path / "test.db")

    director_response = {
        "updated_priorities": "New Priorities Updated",
        "fetch_requests": [{"query": "quantum neural networks", "source_hint": "arxiv"}],
    }
    envelope = {
        "conversation_id": "conv-test",
        "status": "success",
        "response": json.dumps(director_response),
    }

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = ""
    mock_subproc_run.return_value = mock_proc

    success = run_director_step(
        vault_path=str(vault_dir),
        db_path=db_path,
        context_path=str(context_dir),
        output_path=str(output_path),
        timestamp_path=str(timestamp_path),
    )

    assert success is True

    # Output file created
    assert output_path.exists()
    saved_output = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_output["updated_priorities"] == "New Priorities Updated"

    # Vault current-priorities.md updated by director_apply logic
    assert (vault_dir / "current-priorities.md").read_text(encoding="utf-8") == "New Priorities Updated"

    # Shared timestamp file updated
    ts_data = json.loads(timestamp_path.read_text(encoding="utf-8"))
    assert ts_data["curator"] == "2026-08-08T10:00:00"
    assert "director" in ts_data


@patch("research_scanner.director_run.subprocess.run")
def test_run_director_step_malformed_agy_output_logged(mock_subproc_run, tmp_path, caplog):
    """Verify malformed agy output is caught and logged with stderr visible."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "NOT_VALID_JSON"
    mock_proc.stderr = "PermissionDenied: process execution error details"
    mock_subproc_run.return_value = mock_proc

    output_path = tmp_path / "director_output.json"

    with caplog.at_level(logging.ERROR):
        success = run_director_step(output_path=str(output_path))

    assert success is False
    assert "Director CLI output returned unparseable envelope JSON" in caplog.text
    assert "Director CLI stderr: PermissionDenied: process execution error details" in caplog.text


@patch("research_scanner.director_run.subprocess.run")
def test_run_director_step_malformed_inner_json_logged(mock_subproc_run, tmp_path, caplog):
    """Verify malformed inner JSON response is caught and logged with stderr visible."""
    envelope = {
        "status": "success",
        "response": "Inner non-JSON content",
    }
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = "Warning: resource load error"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        success = run_director_step(output_path=str(tmp_path / "output.json"))

    assert success is False
    assert "Director CLI inner response returned unparseable JSON" in caplog.text
    assert "Director CLI stderr: Warning: resource load error" in caplog.text


@patch("research_scanner.director_run.subprocess.run")
def test_run_director_step_schema_validation_failure_logged(mock_subproc_run, tmp_path, caplog):
    """Verify schema validation failure is caught and logged with stderr visible."""
    invalid_schema = {"updated_priorities": 12345}  # int instead of str
    envelope = {
        "status": "success",
        "response": json.dumps(invalid_schema),
    }
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = "Schema mismatch warning on execution"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        success = run_director_step(output_path=str(tmp_path / "output.json"))

    assert success is False
    assert "Schema validation failed: updated_priorities must be a string" in caplog.text
    assert "Director CLI stderr: Schema mismatch warning on execution" in caplog.text


@patch("research_scanner.director_run.subprocess.run")
def test_run_director_step_empty_context_folder(mock_subproc_run, tmp_path):
    """Verify run_director_step works cleanly with an empty context folder."""
    empty_context = tmp_path / "empty_context_dir"
    empty_context.mkdir()

    output_path = tmp_path / "director_output.json"
    timestamp_path = tmp_path / "last_success.json"
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    response_data = {"proactive_message": "Hello from Director!"}
    envelope = {"status": "success", "response": json.dumps(response_data)}

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = ""
    mock_subproc_run.return_value = mock_proc

    with patch("research_scanner.director_apply.send_discord_message", return_value=True):
        success = run_director_step(
            vault_path=str(vault_dir),
            context_path=str(empty_context),
            output_path=str(output_path),
            timestamp_path=str(timestamp_path),
        )

    assert success is True
    assert output_path.exists()
    assert timestamp_path.exists()


@patch("research_scanner.director_run.subprocess.run")
def test_run_director_step_cli_failure_logs_stderr(mock_subproc_run, tmp_path, caplog):
    """Verify non-zero returncode logs stderr in full."""
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ""
    mock_proc.stderr = "Fatal error: unexpected CLI failure"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        success = run_director_step(output_path=str(tmp_path / "output.json"))

    assert success is False
    assert "Director CLI call failed with exit code 1" in caplog.text
    assert "Director CLI stderr: Fatal error: unexpected CLI failure" in caplog.text
