"""
Unit tests for director_apply.py module.
"""

import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from research_scanner import director_apply


def test_director_apply_direct_json(tmp_path):
    """Verify director_apply handles direct JSON files."""
    director_data = {
        "updated_priorities": "1. Test Priority A",
        "fetch_requests": [{"query": "quantum computing", "source_hint": "arxiv"}],
    }
    input_file = tmp_path / "director_direct.json"
    input_file.write_text(json.dumps(director_data), encoding="utf-8")

    test_args = ["director_apply.py", "--input", str(input_file)]
    with patch.object(sys, "argv", test_args):
        with patch("research_scanner.director_apply.config.OBSIDIAN_VAULT_PATH", str(tmp_path)):
            with patch("research_scanner.director_apply.init_db"):
                with patch("research_scanner.director_apply.get_db_connection") as mock_conn_func:
                    mock_conn = MagicMock()
                    mock_conn_func.return_value = mock_conn
                    director_apply.main()

    priorities_path = tmp_path / "current-priorities.md"
    assert priorities_path.exists()
    assert priorities_path.read_text(encoding="utf-8") == "1. Test Priority A"


def test_director_apply_agy_envelope_json(tmp_path):
    """Verify director_apply handles agy JSON envelope format."""
    inner_data = {
        "updated_priorities": "1. Envelope Priority B",
        "fetch_requests": [{"query": "ai alignment", "source_hint": "arxiv"}],
    }
    envelope = {
        "conversation_id": "conv-12345",
        "status": "success",
        "response": json.dumps(inner_data),
    }
    input_file = tmp_path / "director_envelope.json"
    input_file.write_text(json.dumps(envelope), encoding="utf-8")

    test_args = ["director_apply.py", "--input", str(input_file)]
    with patch.object(sys, "argv", test_args):
        with patch("research_scanner.director_apply.config.OBSIDIAN_VAULT_PATH", str(tmp_path)):
            with patch("research_scanner.director_apply.init_db"):
                with patch("research_scanner.director_apply.get_db_connection") as mock_conn_func:
                    mock_conn = MagicMock()
                    mock_conn_func.return_value = mock_conn
                    director_apply.main()

    priorities_path = tmp_path / "current-priorities.md"
    assert priorities_path.exists()
    assert priorities_path.read_text(encoding="utf-8") == "1. Envelope Priority B"


def test_director_apply_agy_envelope_markdown_fenced(tmp_path):
    """Verify director_apply handles agy JSON envelope format with markdown codeblock fences."""
    inner_data = {
        "updated_priorities": "1. Fenced Priority C",
    }
    fenced_response = f"```json\n{json.dumps(inner_data)}\n```"
    envelope = {
        "conversation_id": "conv-67890",
        "status": "success",
        "response": fenced_response,
    }
    input_file = tmp_path / "director_fenced.json"
    input_file.write_text(json.dumps(envelope), encoding="utf-8")

    test_args = ["director_apply.py", "--input", str(input_file)]
    with patch.object(sys, "argv", test_args):
        with patch("research_scanner.director_apply.config.OBSIDIAN_VAULT_PATH", str(tmp_path)):
            director_apply.main()

    priorities_path = tmp_path / "current-priorities.md"
    assert priorities_path.exists()
    assert priorities_path.read_text(encoding="utf-8") == "1. Fenced Priority C"


def test_director_apply_invalid_inner_json_exits(tmp_path):
    """Verify director_apply exits non-zero if envelope response field is invalid JSON."""
    envelope = {
        "conversation_id": "conv-err",
        "status": "success",
        "response": "Invalid inner JSON",
    }
    input_file = tmp_path / "director_invalid_inner.json"
    input_file.write_text(json.dumps(envelope), encoding="utf-8")

    test_args = ["director_apply.py", "--input", str(input_file)]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            director_apply.main()
        assert exc_info.value.code == 1
