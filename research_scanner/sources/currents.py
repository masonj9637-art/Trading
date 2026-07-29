"""
Currents API news data fetcher.
"""

import logging
from typing import List, Dict, Any, Optional
import requests

from research_scanner import config

logger = logging.getLogger("research_scanner.sources.currents")

CURRENTS_SEARCH_URL = "https://api.currentsapi.services/v1/search"


def fetch_currents_items(
    keywords: Optional[List[str]] = None, api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetches tech & industry news items from Currents API matching keywords.

    :param keywords: List of search keywords (defaults to config.NEWS_KEYWORDS)
    :param api_key: Currents API Key (defaults to config.CURRENTS_API_KEY)
    :return: List of normalized item dictionaries
    """
    key = api_key if api_key is not None else config.CURRENTS_API_KEY
    kw_list = keywords if keywords is not None else config.NEWS_KEYWORDS

    if not key:
        logger.warning("CURRENTS_API_KEY is not set. Skipping Currents news fetch.")
        return []

    if not kw_list:
        logger.warning("No keywords configured for Currents API search. Skipping fetch.")
        return []

    kw_query = " ".join(kw_list)
    params = {
        "keywords": kw_query,
        "language": "en",
        "apiKey": key,
    }

    logger.info("Fetching Currents news items for keywords: %s", kw_query)

    try:
        response = requests.get(CURRENTS_SEARCH_URL, params=params, timeout=15)
        if response.status_code != 200:
            logger.warning(
                "Currents API returned status code %d: %s", response.status_code, response.text[:200]
            )
            return []

        data = response.json()
        news_entries = data.get("news", [])
        items: List[Dict[str, Any]] = []

        for entry in news_entries:
            external_id = entry.get("id")
            title = entry.get("title", "").strip()
            url = entry.get("url", "").strip()
            summary = entry.get("description", "").strip()

            if not external_id or not title:
                continue

            items.append(
                {
                    "source": "currents",
                    "external_id": str(external_id),
                    "title": title,
                    "url": url,
                    "summary": summary,
                }
            )

        logger.info("Successfully fetched %d items from Currents API", len(items))
        return items

    except requests.RequestException as e:
        logger.error("Network or HTTP failure while contacting Currents API: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error parsing Currents API response: %s", e, exc_info=True)
        return []
