"""
Unit tests for research_scanner.sources package (arXiv, USPTO, Currents).
"""

from unittest.mock import patch, MagicMock
import pytest

from research_scanner.sources import (
    fetch_arxiv_items,
    fetch_uspto_items,
    fetch_currents_items,
)


def test_fetch_arxiv_items_success():
    mock_feed = MagicMock()
    mock_entry = MagicMock()
    mock_entry.id = "http://arxiv.org/abs/2401.00001v1"
    mock_entry.title = "  Quantum   Computing   Breakthrough  "
    mock_entry.summary = " A new algorithm for quantum simulation. "
    mock_entry.link = "http://arxiv.org/abs/2401.00001v1"
    mock_feed.entries = [mock_entry]

    with patch("feedparser.parse", return_value=mock_feed):
        items = fetch_arxiv_items(categories=["quant-ph"], max_results=1)

    assert len(items) == 1
    assert items[0]["source"] == "arxiv"
    assert items[0]["external_id"] == "2401.00001v1"
    assert items[0]["title"] == "Quantum Computing Breakthrough"
    assert items[0]["summary"] == "A new algorithm for quantum simulation."


def test_fetch_arxiv_items_failure():
    with patch("feedparser.parse", side_effect=Exception("Network error")):
        items = fetch_arxiv_items()
    assert items == []


def test_fetch_uspto_items_missing_key():
    items = fetch_uspto_items(api_key="")
    assert items == []


def test_fetch_uspto_items_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "patentApplications": [
            {
                "applicationMetaData": {
                    "applicationNumberText": "18001122",
                    "inventionTitle": "Robotic Gripper Assembly",
                    "abstractText": "An improved robotic gripper.",
                }
            }
        ]
    }

    with patch("requests.post", return_value=mock_resp):
        items = fetch_uspto_items(cpc_codes=["B25J"], api_key="dummy_uspto_key")

    assert len(items) == 1
    assert items[0]["source"] == "uspto"
    assert items[0]["external_id"] == "18001122"
    assert items[0]["title"] == "Robotic Gripper Assembly"
    assert "https://patentcenter.uspto.gov/applications/18001122" in items[0]["url"]


def test_fetch_uspto_items_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("requests.post", return_value=mock_resp):
        items = fetch_uspto_items(api_key="dummy_uspto_key")

    assert items == []


def test_fetch_currents_items_missing_key():
    items = fetch_currents_items(api_key="")
    assert items == []


def test_fetch_currents_items_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "news": [
            {
                "id": "news_123",
                "title": "New Semiconductor Fab Announced",
                "url": "https://example.com/news/123",
                "description": "A new chip manufacturing facility is open.",
            }
        ]
    }

    with patch("requests.get", return_value=mock_resp):
        items = fetch_currents_items(keywords=["semiconductor"], api_key="dummy_currents_key")

    assert len(items) == 1
    assert items[0]["source"] == "currents"
    assert items[0]["external_id"] == "news_123"
    assert items[0]["title"] == "New Semiconductor Fab Announced"
