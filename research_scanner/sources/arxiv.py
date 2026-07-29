"""
arXiv API data fetcher using feedparser.
"""

import logging
import urllib.parse
from typing import List, Dict, Any, Optional
import feedparser

from research_scanner import config

logger = logging.getLogger("research_scanner.sources.arxiv")


def fetch_arxiv_items(
    categories: Optional[List[str]] = None, max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetches recent papers from arXiv API for specified categories using feedparser.

    :param categories: List of arXiv categories (defaults to config.ARXIV_CATEGORIES)
    :param max_results: Maximum number of results to request per query
    :return: List of normalized item dictionaries
    """
    cats = categories if categories is not None else config.ARXIV_CATEGORIES
    if not cats:
        logger.warning("No arXiv categories configured. Skipping arXiv fetch.")
        return []

    # Construct arXiv search query e.g. cat:quant-ph OR cat:cs.AI OR cat:cs.LG OR cat:cs.RO
    cat_query = " OR ".join([f"cat:{c}" for c in cats])
    params = {
        "search_query": cat_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }

    url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
    logger.info("Fetching arXiv items from %s", url)

    try:
        feed = feedparser.parse(url)
        if getattr(feed, "bozo", 0) and getattr(feed, "bozo_exception", None):
            logger.warning("arXiv feed parser encountered bozo exception: %s", feed.bozo_exception)

        items: List[Dict[str, Any]] = []
        for entry in getattr(feed, "entries", []):
            entry_id = getattr(entry, "id", None) or getattr(entry, "link", "")
            # Extract clean arXiv ID if available
            external_id = entry_id.split("/abs/")[-1] if "/abs/" in entry_id else entry_id

            title = " ".join(getattr(entry, "title", "").split())
            summary = " ".join(getattr(entry, "summary", "").split())
            link = getattr(entry, "link", entry_id)

            if not external_id or not title:
                continue

            items.append(
                {
                    "source": "arxiv",
                    "external_id": external_id,
                    "title": title,
                    "url": link,
                    "summary": summary,
                }
            )

        logger.info("Successfully fetched %d items from arXiv", len(items))
        return items

    except Exception as e:
        logger.error("Failed to fetch or parse arXiv feed: %s", e, exc_info=True)
        return []
