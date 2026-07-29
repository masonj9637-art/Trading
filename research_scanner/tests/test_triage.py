"""
Unit tests for research_scanner.triage module.
"""

from unittest.mock import patch, MagicMock
import pytest

from research_scanner.triage import (
    build_triage_prompt,
    extract_json_payload,
    triage_item,
)


def test_build_triage_prompt():
    item = {
        "source": "arxiv",
        "title": "Quantum Error Correction Bounds",
        "summary": "We establish new theoretical bounds.",
    }
    prompt = build_triage_prompt(item)

    assert "Quantum Error Correction Bounds" in prompt
    assert "Example 1 (Low Notability" in prompt
    assert "Example 2 (High Notability" in prompt
    assert '{"score": int, "reason": str, "category": str}' in prompt.replace("\n", "") or "score" in prompt


def test_extract_json_payload():
    # Direct JSON
    raw1 = '{"score": 8, "reason": "Good paper", "category": "quantum computing"}'
    parsed1 = extract_json_payload(raw1)
    assert parsed1["score"] == 8

    # Markdown wrapped JSON
    raw2 = """```json
    {
        "score": 3,
        "reason": "Minor tweak",
        "category": "ai & machine learning"
    }
    ```"""
    parsed2 = extract_json_payload(raw2)
    assert parsed2["score"] == 3


def test_triage_item_success():
    item = {
        "source": "arxiv",
        "title": "Autonomous Humanoid Robot Bipedal Locomotion",
        "summary": "Demonstrating dynamic stability on rugged terrain.",
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "response": '{"score": 8, "reason": "Strong robotics paper.", "category": "robotics"}'
    }

    with patch("requests.post", return_value=mock_resp):
        res = triage_item(item, ollama_host="http://localhost:11434", model_name="gemma2:2b")

    assert res is not None
    assert res["score"] == 8.0
    assert res["reason"] == "Strong robotics paper."
    assert res["category"] == "robotics"


def test_triage_item_ollama_down():
    item = {"source": "arxiv", "title": "Test", "summary": "Test"}
    with patch("requests.post", side_effect=Exception("Connection refused")):
        res = triage_item(item)
    assert res is None


def test_triage_item_malformed_json():
    item = {"source": "arxiv", "title": "Test", "summary": "Test"}
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "This is not JSON at all."}

    with patch("requests.post", return_value=mock_resp):
        res = triage_item(item)
    assert res is None
