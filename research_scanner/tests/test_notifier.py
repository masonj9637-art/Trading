"""
Unit tests for research_scanner.notifier module.
"""

from unittest.mock import patch, MagicMock
import pytest

from research_scanner.notifier import send_discord_notification


def test_send_discord_notification_missing_credentials():
    candidate = {"title": "Test Title", "score": 8.0}
    res = send_discord_notification(candidate, bot_token="", channel_id="")
    assert res is False


def test_send_discord_notification_success():
    candidate = {
        "title": "Quantum Supremacy",
        "score": 9.0,
        "source": "arxiv",
        "url": "http://arxiv.org/abs/2401.12345",
        "category": "quantum computing",
        "reason": "Major hardware milestone.",
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = send_discord_notification(
            candidate, bot_token="test_token", channel_id="123456789"
        )

    assert res is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "https://discord.com/api/v10/channels/123456789/messages" in args[0]
    assert kwargs["headers"]["Authorization"] == "Bot test_token"
    assert "Quantum Supremacy" in kwargs["json"]["content"]


def test_send_discord_notification_failure():
    candidate = {"title": "Test Title", "score": 8.0}
    with patch("requests.post", side_effect=Exception("Discord API error")):
        res = send_discord_notification(
            candidate, bot_token="test_token", channel_id="123456789"
        )
    assert res is False
