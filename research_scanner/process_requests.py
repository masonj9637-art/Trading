"""
Entrypoint to process director requests.
Polls the director_requests table and executes queries against the corresponding sources.
"""

import sys
import logging
import sqlite3
from typing import Dict, Any, List

from research_scanner import config
from research_scanner.db import (
    get_db_connection,
    init_db,
    compute_item_hash,
    is_item_fetched,
    save_fetched_item,
)
from research_scanner.sources import (
    fetch_arxiv_items,
    fetch_uspto_items,
    fetch_currents_items,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("research_scanner.process_requests")

def run_process_requests(db_path: str = config.DB_PATH) -> None:
    logger.info("--- Starting Process Requests Cycle ---")
    init_db(db_path)

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM director_requests WHERE status = 'pending' ORDER BY requested_at ASC"
        )
        requests = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    if not requests:
        logger.info("No pending requests found.")
        return

    logger.info("Found %d pending requests to process.", len(requests))

    for req in requests:
        req_id = req["id"]
        query = req["query"]
        source_hint = req["source_hint"].lower()
        logger.info("Processing request ID=%d | source=%s | query=%s", req_id, source_hint, query)

        items: List[Dict[str, Any]] = []
        try:
            if source_hint == "arxiv":
                items = fetch_arxiv_items(categories=[query])
            elif source_hint == "uspto":
                items = fetch_uspto_items(cpc_codes=[query])
            elif source_hint == "currents":
                items = fetch_currents_items(keywords=[query])
            else:
                logger.warning("Unknown source_hint '%s' for request ID %d. Skipping.", source_hint, req_id)
                continue
        except Exception as e:
            logger.error("Error fetching items for request ID %d: %s", req_id, e)
            continue

        new_items_count = 0
        for item in items:
            source = item.get("source", "unknown")
            ext_id = item.get("external_id", "")
            if not ext_id:
                continue

            item_hash = compute_item_hash(source, ext_id)
            item["item_hash"] = item_hash
            item["request_id"] = req_id

            if is_item_fetched(db_path, item_hash):
                continue

            if save_fetched_item(db_path, item):
                new_items_count += 1

        new_status = "fetched" if len(items) > 0 else "no_results"
        logger.info("Request ID=%d completed. Found %d items (New: %d). Status: %s", req_id, len(items), new_items_count, new_status)

        conn = get_db_connection(db_path)
        try:
            with conn:
                conn.execute(
                    "UPDATE director_requests SET status = ? WHERE id = ?",
                    (new_status, req_id)
                )
        except Exception as e:
            logger.error("Failed to update status for request ID %d: %s", req_id, e)
        finally:
            conn.close()

    logger.info("--- Process Requests Cycle Complete ---")

if __name__ == "__main__":
    run_process_requests()
