"""
USPTO Patent data fetcher using USPTO Open Data Portal (ODP) API.
"""

import logging
from typing import List, Dict, Any, Optional
import requests

from research_scanner import config

logger = logging.getLogger("research_scanner.sources.uspto")

USPTO_SEARCH_URL = "https://api.uspto.gov/api/v1/patent/applications/search"


def fetch_uspto_items(
    cpc_codes: Optional[List[str]] = None, api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetches patent application data filtered by CPC classification codes from the USPTO Open Data Portal.

    :param cpc_codes: List of CPC classification codes (defaults to config.PATENT_CPC_CODES)
    :param api_key: USPTO API Key (defaults to config.USPTO_API_KEY)
    :return: List of normalized item dictionaries
    """
    key = api_key if api_key is not None else config.USPTO_API_KEY
    codes = cpc_codes if cpc_codes is not None else config.PATENT_CPC_CODES

    if not key:
        logger.warning("USPTO_API_KEY is not set. Skipping USPTO patent fetch.")
        return []

    if not codes:
        logger.warning("No USPTO CPC codes configured. Skipping USPTO patent fetch.")
        return []

    headers = {
        "X-API-KEY": key,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "ResearchScanner/1.0",
    }

    payload = {
        "filters": [
            {
                "name": "applicationMetaData.cpcClassificationBag",
                "value": codes,
            }
        ],
        "sort": [{"field": "applicationDate", "order": "desc"}],
        "pagination": {"offset": 0, "limit": 25},
    }

    logger.info("Fetching USPTO patent items with CPC codes %s", codes)

    try:
        response = requests.post(USPTO_SEARCH_URL, headers=headers, json=payload, timeout=15)
        if response.status_code != 200:
            logger.warning(
                "USPTO API returned status code %d: %s", response.status_code, response.text[:200]
            )
            return []

        data = response.json()
        items: List[Dict[str, Any]] = []

        # Parse application records from API response
        records = data.get("patentApplications") or data.get("results") or data.get("applications") or []
        for rec in records:
            meta = rec.get("applicationMetaData", rec)
            app_num = meta.get("applicationNumberText") or rec.get("applicationNumber") or rec.get("id")
            title = meta.get("inventionTitle") or rec.get("title") or ""
            abstract = meta.get("abstractText") or rec.get("abstract") or rec.get("summary") or ""

            if not app_num or not title:
                continue

            clean_app_num = str(app_num).strip()
            url = f"https://patentcenter.uspto.gov/applications/{clean_app_num}"

            items.append(
                {
                    "source": "uspto",
                    "external_id": clean_app_num,
                    "title": title.strip(),
                    "url": url,
                    "summary": abstract.strip(),
                }
            )

        logger.info("Successfully fetched %d items from USPTO API", len(items))
        return items

    except requests.RequestException as e:
        logger.error("Network or HTTP failure while contacting USPTO API: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error parsing USPTO API response: %s", e, exc_info=True)
        return []
