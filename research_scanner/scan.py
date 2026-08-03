"""
Main scan entrypoint for research_scanner.
Runs one full fetch -> deduplicate -> triage -> candidate store -> notification cycle.
Designed to be executed on a schedule via cron.
"""

import sys
import logging
from typing import Dict, Any, List

from research_scanner import config
from research_scanner.db import (
    init_db,
    compute_item_hash,
    is_item_fetched,
    save_fetched_item,
)
from research_scanner.sources import (
    fetch_arxiv_items,
    fetch_uspto_items,
    fetch_currents_items,
    fetch_openalex_items,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("research_scanner.scan")


def run_scan_cycle(db_path: str = config.DB_PATH) -> Dict[str, int]:
    """
    Executes one full fetch + triage cycle across all configured data sources.

    :param db_path: Path to SQLite database file
    :return: Summary metrics dict
    """
    logger.info("--- Starting Research Scanner Cycle ---")
    logger.info("Config: DB=%s", db_path)

    # Step 1: Ensure SQLite database and tables exist
    init_db(db_path)

    # Step 2: Fetch items from all sources
    all_items: List[Dict[str, Any]] = []

    try:
        arxiv_items = fetch_arxiv_items()
        all_items.extend(arxiv_items)
    except Exception as e:
        logger.error("Error fetching arXiv items: %s", e)

    try:
        uspto_items = fetch_uspto_items()
        all_items.extend(uspto_items)
    except Exception as e:
        logger.error("Error fetching USPTO items: %s", e)

    try:
        currents_items = fetch_currents_items()
        all_items.extend(currents_items)
    except Exception as e:
        logger.error("Error fetching Currents items: %s", e)

    try:
        openalex_items = fetch_openalex_items()
        all_items.extend(openalex_items)
    except Exception as e:
        logger.error("Error fetching OpenAlex items: %s", e)

    logger.info("Total items retrieved from sources: %d", len(all_items))

    # Step 3: Process items (deduplicate)
    stats = {
        "fetched": len(all_items),
        "new": 0,
    }

    for item in all_items:
        source = item.get("source", "unknown")
        ext_id = item.get("external_id", "")
        if not ext_id:
            continue

        item_hash = compute_item_hash(source, ext_id)
        item["item_hash"] = item_hash

        # Deduplication check
        if is_item_fetched(db_path, item_hash):
            logger.debug("Skipping already processed item: %s:%s", source, ext_id)
            continue

        # Save new raw item
        saved = save_fetched_item(db_path, item)
        if not saved:
            continue

        stats["new"] += 1

    logger.info(
        "--- Scan Cycle Complete --- Stats: Fetched=%d | New=%d",
        stats["fetched"],
        stats["new"],
    )
    return stats


if __name__ == "__main__":
    run_scan_cycle()
