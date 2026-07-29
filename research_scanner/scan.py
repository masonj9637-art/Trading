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
    save_candidate,
)
from research_scanner.sources import (
    fetch_arxiv_items,
    fetch_uspto_items,
    fetch_currents_items,
)
from research_scanner.triage import triage_item
from research_scanner.notifier import send_discord_notification

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
    logger.info("Config: DB=%s | Ollama Host=%s | Model=%s | Threshold=%.1f", db_path, config.OLLAMA_HOST, config.GEMMA_MODEL, config.SCORE_THRESHOLD)

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

    logger.info("Total items retrieved from sources: %d", len(all_items))

    # Step 3: Process items (deduplicate, triage, save candidates, notify)
    stats = {
        "fetched": len(all_items),
        "new": 0,
        "triaged": 0,
        "candidates": 0,
        "notifications_sent": 0,
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

        # LLM Triage step via local Ollama
        triage_res = triage_item(item, config.OLLAMA_HOST, config.GEMMA_MODEL)
        if triage_res is None:
            logger.warning("Skipping candidate evaluation for '%s' due to triage failure.", item.get("title"))
            continue

        stats["triaged"] += 1

        score = triage_res["score"]
        reason = triage_res["reason"]
        category = triage_res["category"]

        # Check threshold
        if score >= config.SCORE_THRESHOLD:
            stats["candidates"] += 1
            candidate = dict(item)
            candidate["score"] = score
            candidate["reason"] = reason
            candidate["category"] = category

            # Save candidate record
            save_candidate(db_path, candidate)

            # Dispatch notification
            notified = send_discord_notification(candidate)
            if notified:
                stats["notifications_sent"] += 1

    logger.info(
        "--- Scan Cycle Complete --- Stats: Fetched=%d | New=%d | Triaged=%d | Candidates=%d | Notified=%d",
        stats["fetched"],
        stats["new"],
        stats["triaged"],
        stats["candidates"],
        stats["notifications_sent"],
    )
    return stats


if __name__ == "__main__":
    run_scan_cycle()
