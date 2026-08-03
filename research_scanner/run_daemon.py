"""
Continuous daemon runner for research_scanner.
Runs fetch -> process requests -> export to obsidian -> rebuild vault index in a continuous loop.
"""

import argparse
import logging
import sys
import time
from datetime import datetime

from research_scanner import config
from research_scanner.scan import run_scan_cycle
from research_scanner.process_requests import run_process_requests
from research_scanner.export_to_obsidian import export_unreviewed_candidates
from research_scanner.build_vault_index import build_vault_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("research_scanner.daemon")


def run_continuous_daemon(interval_seconds: int = 1800, vault_path: str = config.OBSIDIAN_VAULT_PATH) -> None:
    """
    Executes the research_scanner pipeline continuously every interval_seconds.

    :param interval_seconds: Time to sleep between scan iterations (default: 1800s / 30 min)
    :param vault_path: Path to target Obsidian vault
    """
    logger.info("==================================================")
    logger.info("   RESEARCH SCANNER CONTINUOUS DAEMON STARTED     ")
    logger.info("   Interval: %d seconds (%d minutes)            ", interval_seconds, interval_seconds // 60)
    logger.info("   Vault: %s                                      ", vault_path)
    logger.info("==================================================")

    iteration = 1
    while True:
        logger.info("--- Starting Cycle #%d at %s ---", iteration, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            # Step 1: Run raw fetch & deduplication cycle
            scan_stats = run_scan_cycle()
            logger.info("Scan cycle #%d stats: %s", iteration, scan_stats)

            # Step 2: Process queued director requests
            run_process_requests()

            # Step 3: Export unreviewed candidates to Obsidian vault
            export_stats = export_unreviewed_candidates(vault_path=vault_path, min_score=0.0)
            logger.info("Obsidian export stats: %s", export_stats)

            # Step 4: Rebuild Obsidian vault index
            build_vault_index(vault_path)
            logger.info("Obsidian vault index rebuilt.")

        except KeyboardInterrupt:
            logger.info("Daemon execution stopped by user (KeyboardInterrupt). Exiting.")
            sys.exit(0)
        except Exception as e:
            logger.error("Error during daemon cycle #%d: %s", iteration, e, exc_info=True)

        logger.info("Cycle #%d complete. Sleeping for %d seconds...", iteration, interval_seconds)
        time.sleep(interval_seconds)
        iteration += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuous background daemon for research_scanner.")
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="Scan interval in seconds (default: 1800 = 30 minutes)",
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=config.OBSIDIAN_VAULT_PATH,
        help=f"Target Obsidian vault path (default: {config.OBSIDIAN_VAULT_PATH})",
    )
    args = parser.parse_args()

    run_continuous_daemon(interval_seconds=args.interval, vault_path=args.vault)


if __name__ == "__main__":
    main()
