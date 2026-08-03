"""
Discord REST notification dispatcher for research_scanner.
"""

import logging
from typing import Dict, Any, Optional
import requests

from research_scanner import config

logger = logging.getLogger("research_scanner.notifier")


def send_discord_notification(
    candidate: Dict[str, Any],
    bot_token: Optional[str] = None,
    channel_id: Optional[str] = None,
    timeout: int = 10,
) -> bool:
    """
    Sends a Discord notification via direct REST POST to the specified channel.

    :param candidate: Candidate dictionary containing title, score, source, url, category, reason
    :param bot_token: Discord Bot token (defaults to config.DISCORD_BOT_TOKEN)
    :param channel_id: Discord Channel ID (defaults to config.DISCORD_CHANNEL_ID)
    :param timeout: Request timeout in seconds
    :return: True if notification sent successfully, False otherwise
    """
    token = bot_token if bot_token is not None else config.DISCORD_BOT_TOKEN
    cid = channel_id if channel_id is not None else config.DISCORD_CHANNEL_ID

    if not token or not cid:
        logger.warning(
            "DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID missing. Skipping Discord notification for '%s'",
            candidate.get("title"),
        )
        return False

    url = f"https://discord.com/api/v10/channels/{cid}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
        "User-Agent": "ResearchScanner/1.0",
    }

    title = candidate.get("title", "Untitled")
    score = candidate.get("score", 0.0)
    source = candidate.get("source", "unknown").upper()
    item_url = candidate.get("url", "")
    category = candidate.get("category", "general")
    reason = candidate.get("reason", "")

    content = (
        f"🚨 **Research Candidate Alert** (Score: **{score:.1f}/10**)\n"
        f"**Title**: {title}\n"
        f"**Source**: {source} | **Category**: {category}\n"
        f"**Reason**: {reason}\n"
        f"**URL**: {item_url}"
    )

    payload = {"content": content}

    try:
        logger.info("Sending Discord REST notification for '%s' (Score: %.1f)", title, score)
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)

        if response.status_code in (200, 201):
            logger.info("Discord notification sent successfully for candidate '%s'", title)
            return True
        else:
            logger.warning(
                "Discord API returned status %d: %s", response.status_code, response.text[:200]
            )
            return False

    except requests.RequestException as e:
        logger.error("Network or HTTP failure sending Discord notification: %s", e)
        return False
    except Exception as e:
        logger.error("Unexpected error in send_discord_notification: %s", e, exc_info=True)
        return False


def send_discord_message(
    content: str,
    bot_token: Optional[str] = None,
    channel_id: Optional[str] = None,
    timeout: int = 10,
) -> bool:
    """
    Sends a plain string message to Discord via REST POST.

    :param content: The plain text message to send
    :param bot_token: Discord Bot token (defaults to config.DISCORD_BOT_TOKEN)
    :param channel_id: Discord Channel ID (defaults to config.DISCORD_CHANNEL_ID)
    :param timeout: Request timeout in seconds
    :return: True if message sent successfully, False otherwise
    """
    token = bot_token if bot_token is not None else config.DISCORD_BOT_TOKEN
    cid = channel_id if channel_id is not None else config.DISCORD_CHANNEL_ID

    if not token or not cid:
        logger.warning(
            "DISCORD_BOT_TOKEN or DISCORD_CHANNEL_ID missing. Skipping Discord message."
        )
        return False

    url = f"https://discord.com/api/v10/channels/{cid}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
        "User-Agent": "ResearchScanner/1.0",
    }

    payload = {"content": content}

    try:
        logger.info("Sending Discord REST message")
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)

        if response.status_code in (200, 201):
            logger.info("Discord message sent successfully")
            return True
        else:
            logger.warning(
                "Discord API returned status %d: %s", response.status_code, response.text[:200]
            )
            return False

    except requests.RequestException as e:
        logger.error("Network or HTTP failure sending Discord message: %s", e)
        return False
    except Exception as e:
        logger.error("Unexpected error in send_discord_message: %s", e, exc_info=True)
        return False
