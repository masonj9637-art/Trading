"""
OpenAlex API data fetcher for global research papers, preprints, and patents.
OpenAlex is completely open, free, and keyless.
"""

import logging
from typing import List, Dict, Any, Optional
import requests

from research_scanner import config

logger = logging.getLogger("research_scanner.sources.openalex")

OPENALEX_WORKS_URL = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> str:
    """
    Reconstructs clean text summary from OpenAlex's abstract_inverted_index.

    :param inverted_index: Dictionary mapping words to lists of integer position indices.
    :return: Reconstructed string paragraph.
    """
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""

    word_positions = []
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                if isinstance(pos, int):
                    word_positions.append((pos, word))

    word_positions.sort(key=lambda x: x[0])
    return " ".join(w[1] for w in word_positions)


def fetch_openalex_items(
    keywords: Optional[List[str]] = None, per_page: int = 25
) -> List[Dict[str, Any]]:
    """
    Fetches recent patents, preprints, and research items from OpenAlex matching keywords.

    :param keywords: List of search keywords (defaults to config.NEWS_KEYWORDS)
    :param per_page: Maximum number of items to retrieve per fetch
    :return: List of normalized item dictionaries
    """
    kw_list = keywords if keywords is not None else config.NEWS_KEYWORDS
    if not kw_list:
        logger.warning("No keywords configured for OpenAlex search. Skipping fetch.")
        return []

    kw_query = " OR ".join(f'"{kw}"' for kw in kw_list)
    params = {
        "search": kw_query,
        "sort": "publication_date:desc",
        "per-page": per_page,
        "mailto": getattr(config, "OPENALEX_MAILTO", "research_scanner@example.com"),
    }

    headers = {
        "User-Agent": f"ResearchScanner/1.0 (mailto:{getattr(config, 'OPENALEX_MAILTO', 'research_scanner@example.com')})"
    }

    logger.info("Fetching OpenAlex items for query: %s", kw_query)

    try:
        response = requests.get(OPENALEX_WORKS_URL, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            logger.warning(
                "OpenAlex API returned status code %d: %s", response.status_code, response.text[:200]
            )
            return []

        data = response.json()
        results = data.get("results", [])
        items: List[Dict[str, Any]] = []

        for work in results:
            openalex_id = work.get("id", "")
            # Extract clean ID e.g. W123456789 from https://openalex.org/W123456789
            clean_id = openalex_id.split("/")[-1] if "/" in openalex_id else openalex_id
            title = work.get("title", "") or ""
            doi = work.get("doi") or work.get("id") or ""
            
            # Reconstruct abstract summary
            inverted_index = work.get("abstract_inverted_index")
            summary = reconstruct_abstract(inverted_index)

            if not clean_id or not title:
                continue

            items.append(
                {
                    "source": "openalex",
                    "external_id": clean_id,
                    "title": title.strip(),
                    "url": doi.strip(),
                    "summary": summary.strip(),
                }
            )

        logger.info("Successfully fetched %d items from OpenAlex API", len(items))
        return items

    except requests.RequestException as e:
        logger.error("Network or HTTP failure while contacting OpenAlex API: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error parsing OpenAlex API response: %s", e, exc_info=True)
        return []
