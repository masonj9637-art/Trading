"""
Unit tests for run_daemon.py module.
"""

import json
import logging
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

try:
    from research_scanner.run_daemon import (
        is_quota_error,
        get_curator_prompt,
        get_agy_executable_path,
        run_curator_export_step,
        run_single_cycle,
        run_continuous_daemon,
        main,
        CURATOR_TASK_PROMPT,
    )
except ImportError:
    from run_daemon import (
        is_quota_error,
        get_curator_prompt,
        get_agy_executable_path,
        run_curator_export_step,
        run_single_cycle,
        run_continuous_daemon,
        main,
        CURATOR_TASK_PROMPT,
    )


class StopLoopException(Exception):
    pass


def test_get_agy_executable_path_default():
    """Verify get_agy_executable_path returns default path when AGY_EXECUTABLE_PATH is not set and which returns None."""
    with patch.dict(os.environ, {}, clear=True), patch("shutil.which", return_value=None):
        assert get_agy_executable_path() == r"C:\Users\mason\AppData\Local\agy\bin\agy.exe"


def test_get_agy_executable_path_which_discovery():
    """Verify get_agy_executable_path returns path discovered by shutil.which when AGY_EXECUTABLE_PATH is not set."""
    with patch.dict(os.environ, {}, clear=True), patch("shutil.which", return_value=r"C:\discovered\agy.exe"):
        assert get_agy_executable_path() == r"C:\discovered\agy.exe"


def test_get_agy_executable_path_env_override():
    """Verify get_agy_executable_path honors AGY_EXECUTABLE_PATH environment variable."""
    with patch.dict(os.environ, {"AGY_EXECUTABLE_PATH": r"C:\custom\path\agy.exe"}):
        assert get_agy_executable_path() == r"C:\custom\path\agy.exe"


def test_is_quota_error_detection():
    """Verify quota/rate-limit error detection keywords."""
    assert is_quota_error(stderr="HTTP 429 Too Many Requests") is True
    assert is_quota_error(stderr="Quota exceeded for model") is True
    assert is_quota_error(stderr="RESOURCE_EXHAUSTED: rate limit hit") is True
    assert is_quota_error(stderr="Error 429: ratelimit") is True

    assert is_quota_error(stderr="Segmentation fault (core dumped)") is False
    assert is_quota_error(stderr="FileNotFoundError: no file") is False
    assert is_quota_error(stderr="SyntaxError: invalid syntax") is False


@patch("research_scanner.run_daemon.get_unconsumed_items")
def test_get_curator_prompt(mock_get_unconsumed, tmp_path):
    """Verify curator prompt retrieval with embedded unconsumed items and priorities."""
    mock_get_unconsumed.return_value = [
        {
            "id": 42,
            "source": "arxiv",
            "title": "Quantum Supremacy in 2026",
            "summary": "Demonstration of quantum speedup.",
            "url": "https://arxiv.org/abs/2608.12345",
            "fetched_at": "2026-08-08 10:00:00",
            "request_id": 7,
        }
    ]
    priorities_file = tmp_path / "current-priorities.md"
    priorities_file.write_text("Director Priority: Quantum Benchmarks.", encoding="utf-8")

    prompt, item_ids = get_curator_prompt(db_path="/tmp/test.db", vault_path=str(tmp_path))
    assert "You are Curator" in prompt
    assert "Director Priority: Quantum Benchmarks." in prompt
    assert "Quantum Supremacy in 2026" in prompt
    assert "Demonstration of quantum speedup." in prompt
    assert "https://arxiv.org/abs/2608.12345" in prompt
    assert item_ids == [42]


@patch("research_scanner.run_daemon.get_unconsumed_items")
@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_success_envelope(mock_export, mock_subproc_run, mock_get_unconsumed, tmp_path):
    """Verify successful Curator CLI run with agy JSON envelope format."""
    mock_get_unconsumed.return_value = [
        {
            "id": 1,
            "source": "arxiv",
            "title": "Quantum Computing Advances",
            "summary": "Latest paper summary.",
            "url": "http://arxiv.org/abs/123",
            "fetched_at": "2026-08-08 10:00:00",
            "request_id": None,
        }
    ]
    decisions = [
        {
            "fetched_item_id": 1,
            "category": "quantum computing",
            "reasoning": "Directly aligns with quantum priorities.",
        }
    ]
    envelope = {
        "conversation_id": "conv-12345",
        "status": "success",
        "response": json.dumps(decisions),
    }
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = ""
    mock_subproc_run.return_value = mock_proc

    mock_export.return_value = {"found": 1, "exported": 1, "failed": 0}

    stats = run_curator_export_step(vault_path=str(tmp_path))

    assert stats == {"found": 1, "exported": 1, "failed": 0}
    assert mock_subproc_run.called
    call_args = mock_subproc_run.call_args[0][0]
    assert call_args[0] == get_agy_executable_path()
    assert call_args[1] == "--add-dir"
    assert len(call_args[2]) > 0
    assert call_args[3] == "--output-format"
    assert call_args[4] == "json"

    prompt_arg = mock_subproc_run.call_args[1]["input"]
    assert "You are Curator" in prompt_arg
    assert "Quantum Computing Advances" in prompt_arg
    assert "Latest paper summary." in prompt_arg

    assert mock_export.called
    decisions_path = mock_export.call_args[0][0]
    assert decisions_path == "curator_decisions.json"
    if os.path.exists("curator_decisions.json"):
        os.remove("curator_decisions.json")


@patch("research_scanner.run_daemon.subprocess.run", side_effect=FileNotFoundError)
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_file_not_found(mock_export, mock_subproc_run, caplog):
    """Verify FileNotFoundError handler logs the exact attempted path."""
    expected_path = get_agy_executable_path()
    with caplog.at_level(logging.ERROR):
        stats = run_curator_export_step()

    assert stats is None
    assert mock_export.called is False
    assert f"Curator CLI call failed: 'agy' executable not found at path '{expected_path}'." in caplog.text


@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_success_envelope_markdown_fenced(mock_export, mock_subproc_run, tmp_path):
    """Verify successful Curator CLI run with markdown codeblock fences inside inner response."""
    decisions = [
        {
            "fetched_item_id": 2,
            "category": "ai safety",
            "reasoning": "Fits priorities.",
        }
    ]
    fenced_response = f"```json\n{json.dumps(decisions)}\n```"
    envelope = {
        "conversation_id": "conv-67890",
        "status": "success",
        "response": fenced_response,
    }
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = ""
    mock_subproc_run.return_value = mock_proc

    mock_export.return_value = {"found": 1, "exported": 1, "failed": 0}

    stats = run_curator_export_step(vault_path=str(tmp_path))

    assert stats == {"found": 1, "exported": 1, "failed": 0}
    if os.path.exists("curator_decisions.json"):
        os.remove("curator_decisions.json")


@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_quota_exhausted(mock_export, mock_subproc_run, caplog):
    """Verify quota failure is detected and logged distinctly, skipping export."""
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ""
    mock_proc.stderr = "Error 429: RESOURCE_EXHAUSTED - Quota limit reached"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        stats = run_curator_export_step()

    assert stats is None
    assert mock_export.called is False
    assert "QUOTA EXHAUSTED - Curator call skipped this cycle" in caplog.text


@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_generic_cli_failure(mock_export, mock_subproc_run, caplog):
    """Verify generic CLI error logs an ERROR and skips export without quota message."""
    mock_proc = MagicMock()
    mock_proc.returncode = 127
    mock_proc.stdout = ""
    mock_proc.stderr = "Command not found or internal system fault"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        stats = run_curator_export_step()

    assert stats is None
    assert mock_export.called is False
    assert "Curator CLI call failed with exit code 127" in caplog.text
    assert "QUOTA EXHAUSTED" not in caplog.text


@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_empty_output_logs_stderr(mock_export, mock_subproc_run, caplog):
    """Verify empty stdout logs error and Curator CLI stderr in full."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = ""
    mock_proc.stderr = "PermissionDenied: command access denied"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        stats = run_curator_export_step()

    assert stats is None
    assert mock_export.called is False
    assert "Curator CLI returned empty output." in caplog.text
    assert "Curator CLI stderr: PermissionDenied: command access denied" in caplog.text


@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_unparseable_envelope_json(mock_export, mock_subproc_run, caplog):
    """Verify unparseable envelope JSON output logs an ERROR, raw output, and stderr."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "This is not valid JSON content."
    mock_proc.stderr = "PermissionDenied: command access denied"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        stats = run_curator_export_step()

    assert stats is None
    assert mock_export.called is False
    assert "Curator CLI output returned unparseable envelope JSON" in caplog.text
    assert "Raw Curator output that failed to parse: This is not valid JSON content." in caplog.text
    assert "Curator CLI stderr: PermissionDenied: command access denied" in caplog.text


@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_unparseable_inner_json(mock_export, mock_subproc_run, caplog):
    """Verify unparseable inner response JSON logs inner response error, raw response, and stderr."""
    envelope = {
        "conversation_id": "conv-999",
        "status": "success",
        "response": "This is not valid inner JSON text.",
    }
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = "Warning: low disk space"
    mock_subproc_run.return_value = mock_proc

    with caplog.at_level(logging.ERROR):
        stats = run_curator_export_step()

    assert stats is None
    assert mock_export.called is False
    assert "Curator CLI inner response returned unparseable JSON" in caplog.text
    assert "Raw Curator output that failed to parse: This is not valid inner JSON text." in caplog.text
    assert "Curator CLI stderr: Warning: low disk space" in caplog.text


@patch("research_scanner.run_daemon.run_scan_cycle")
@patch("research_scanner.run_daemon.run_process_requests")
@patch("research_scanner.run_daemon.run_curator_export_step")
@patch("research_scanner.run_daemon.build_vault_index")
@patch("research_scanner.run_daemon.time.sleep", side_effect=StopLoopException)
def test_run_continuous_daemon_cycle_execution(
    mock_sleep, mock_build_index, mock_curator_export, mock_process_requests, mock_scan_cycle
):
    """Verify full daemon loop executes steps 1-4 in sequence."""
    mock_scan_cycle.return_value = {"arxiv": 5}

    with pytest.raises(StopLoopException):
        run_continuous_daemon(interval_seconds=1800, vault_path="/tmp/test_vault")

    assert mock_scan_cycle.called
    assert mock_process_requests.called
    assert mock_curator_export.called
    assert mock_curator_export.call_args[1] == {"vault_path": "/tmp/test_vault", "db_path": "research_scanner.db"}
    assert mock_build_index.called
    assert mock_build_index.call_args[0][0] == "/tmp/test_vault"


@patch("research_scanner.run_daemon.run_scan_cycle", side_effect=KeyboardInterrupt)
def test_run_continuous_daemon_keyboard_interrupt(mock_scan_cycle):
    """Verify KeyboardInterrupt gracefully exits continuous daemon."""
    with pytest.raises(SystemExit) as exc_info:
        run_continuous_daemon()
    assert exc_info.value.code == 0


@patch("research_scanner.run_daemon.run_scan_cycle")
@patch("research_scanner.run_daemon.run_process_requests")
@patch("research_scanner.run_daemon.run_curator_export_step")
@patch("research_scanner.run_daemon.build_vault_index")
def test_run_single_cycle(
    mock_build_index, mock_curator_export, mock_process_requests, mock_scan_cycle
):
    """Verify run_single_cycle executes steps 1-4 once in sequence."""
    mock_scan_cycle.return_value = {"arxiv": 3}

    run_single_cycle(vault_path="/tmp/test_single_vault", iteration=1)

    assert mock_scan_cycle.called
    assert mock_process_requests.called
    assert mock_curator_export.called
    assert mock_curator_export.call_args[1] == {"vault_path": "/tmp/test_single_vault", "db_path": "research_scanner.db"}
    assert mock_build_index.called
    assert mock_build_index.call_args[0][0] == "/tmp/test_single_vault"


@patch("research_scanner.run_daemon.run_single_cycle")
@patch("research_scanner.run_daemon.run_continuous_daemon")
def test_main_once_flag(mock_continuous_daemon, mock_single_cycle):
    """Verify main() with --once runs exactly one cycle and exits without entering continuous loop."""
    test_args = ["run_daemon.py", "--once", "--vault", "/tmp/once_vault"]
    with patch.object(sys, "argv", test_args):
        main()

    assert mock_single_cycle.called
    assert mock_single_cycle.call_count == 1
    assert mock_single_cycle.call_args[1] == {"vault_path": "/tmp/once_vault", "db_path": "research_scanner.db"}
    assert not mock_continuous_daemon.called


@patch("research_scanner.run_daemon.run_single_cycle")
@patch("research_scanner.run_daemon.run_continuous_daemon")
def test_main_default_continuous(mock_continuous_daemon, mock_single_cycle):
    """Verify main() without --once invokes continuous daemon."""
    test_args = ["run_daemon.py", "--interval", "600", "--vault", "/tmp/cont_vault"]
    with patch.object(sys, "argv", test_args):
        main()

    assert mock_continuous_daemon.called
    assert mock_continuous_daemon.call_args[1] == {
        "interval_seconds": 600,
        "vault_path": "/tmp/cont_vault",
        "db_path": "research_scanner.db",
    }
    assert not mock_single_cycle.called


@patch("research_scanner.run_daemon.subprocess.run")
def test_curator_export_decisions_outcomes(mock_subproc_run, tmp_path):
    """Verify that promoted items become 'promoted', unpromoted items sent become 'reviewed_not_promoted', and unsent items remain unconsumed."""
    from research_scanner.db import init_db, save_fetched_item, get_fetched_item_by_id

    db_path = str(tmp_path / "test_outcomes.db")
    vault_path = str(tmp_path / "vault")
    os.makedirs(vault_path, exist_ok=True)
    init_db(db_path)

    item1 = {"source": "arxiv", "external_id": "item-1", "title": "Promoted Paper", "summary": "Sum 1", "url": "http://1"}
    item2 = {"source": "arxiv", "external_id": "item-2", "title": "Rejected Paper", "summary": "Sum 2", "url": "http://2"}
    save_fetched_item(db_path, item1)
    save_fetched_item(db_path, item2)

    # Item IDs in DB will be 1 and 2
    decisions = [
        {
            "fetched_item_id": 1,
            "category": "quantum",
            "reasoning": "Fits priorities well.",
        }
    ]
    envelope = {
        "status": "success",
        "response": json.dumps(decisions),
    }
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = json.dumps(envelope)
    mock_proc.stderr = ""
    mock_subproc_run.return_value = mock_proc

    stats = run_curator_export_step(vault_path=vault_path, db_path=db_path)

    # Item 3 is saved after Curator cycle (never sent to Curator)
    item3 = {"source": "arxiv", "external_id": "item-3", "title": "Unsent Paper", "summary": "Sum 3", "url": "http://3"}
    save_fetched_item(db_path, item3)

    assert stats == {"found": 1, "exported": 1, "failed": 0}

    # Verify Item 1 (promoted)
    f1 = get_fetched_item_by_id(db_path, 1)
    assert f1["consumed_by_curator"] == 1
    assert f1["curator_decision"] == "promoted"

    # Verify Item 2 (sent but not promoted)
    f2 = get_fetched_item_by_id(db_path, 2)
    assert f2["consumed_by_curator"] == 1
    assert f2["curator_decision"] == "reviewed_not_promoted"

    # Verify Item 3 (never sent)
    f3 = get_fetched_item_by_id(db_path, 3)
    assert f3["consumed_by_curator"] == 0 or f3["consumed_by_curator"] is None
    assert f3["curator_decision"] is None

    if os.path.exists("curator_decisions.json"):
        os.remove("curator_decisions.json")


@patch("research_scanner.run_daemon.get_unconsumed_items")
@patch("research_scanner.run_daemon.subprocess.run")
@patch("research_scanner.run_daemon.export_from_curator_decisions")
def test_run_curator_export_step_unicode_prompt_handling(mock_export, mock_subproc_run, mock_get_unconsumed, tmp_path):
    """Verify run_curator_export_step passes encoding='utf-8' to subprocess.run when prompt contains non-ASCII characters (e.g. ω, café)."""
    unicode_title = "Quantum Algorithm ω for café & π-pulse"
    mock_get_unconsumed.return_value = [
        {
            "id": 99,
            "source": "arxiv",
            "title": unicode_title,
            "summary": "Study on ω-qubit decoherence.",
            "url": "http://arxiv.org/abs/omega",
            "fetched_at": "2026-08-08 10:00:00",
            "request_id": None,
        }
    ]
    decisions = [
        {
            "fetched_item_id": 99,
            "category": "quantum",
            "reasoning": "Fits priorities for ω-qubits.",
        }
    ]
    envelope = {
        "status": "success",
        "response": json.dumps(decisions),
    }

    def side_effect(cmd, input=None, capture_output=True, text=True, encoding=None, **kwargs):
        enc = encoding if encoding is not None else ("cp1252" if os.name == "nt" else "utf-8")
        if text and input is not None:
            input.encode(enc)
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = json.dumps(envelope)
        proc.stderr = ""
        return proc

    mock_subproc_run.side_effect = side_effect
    mock_export.return_value = {"found": 1, "exported": 1, "failed": 0}

    priorities_file = tmp_path / "current-priorities.md"
    priorities_file.write_text("Priority for café research with Greek letter ω.", encoding="utf-8")

    stats = run_curator_export_step(vault_path=str(tmp_path))

    assert stats == {"found": 1, "exported": 1, "failed": 0}
    assert mock_subproc_run.called
    kwargs = mock_subproc_run.call_args[1]
    assert kwargs.get("encoding") == "utf-8"
    assert "ω" in kwargs.get("input")
    assert "café" in kwargs.get("input")

    if os.path.exists("curator_decisions.json"):
        os.remove("curator_decisions.json")



