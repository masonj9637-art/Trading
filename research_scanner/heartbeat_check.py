"""
Heartbeat monitor for research_scanner scheduled jobs.
Checks research_scanner/last_success.json and sends Discord alert if any component goes silent.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from research_scanner import config
from research_scanner import notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("research_scanner.heartbeat_check")

# Component max allowed ages in hours before alerting
COMPONENTS_THRESHOLDS: Dict[str, float] = {
    "scan_and_curator": 6.0,
    "director": 8.0,
}


def parse_iso_timestamp(ts_str: str) -> Optional[datetime]:
    """
    Parses an ISO 8601 timestamp string into a datetime object.
    Returns None if parsing fails.
    """
    if not ts_str or not isinstance(ts_str, str):
        return None
    try:
        clean_str = ts_str.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception:
        return None


def get_timestamp_age_seconds(dt: datetime, now: Optional[datetime] = None) -> float:
    """
    Calculates age in seconds from dt to now.
    Handles naive vs aware datetimes safely.
    """
    if dt is None:
        return float("inf")

    if dt.tzinfo is not None:
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
    else:
        if now is None:
            now = datetime.now()
        elif now.tzinfo is not None:
            now = now.astimezone().replace(tzinfo=None)

    delta = now - dt
    return delta.total_seconds()


def check_heartbeat(
    filepath: Optional[str] = None,
    now: Optional[datetime] = None,
    send_discord: bool = True,
    bot_token: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reads last_success.json and verifies that scan_and_curator (<= 6h) and director (<= 8h)
    have updated their timestamps recently.

    If any component is missing or stale, sends a Discord alert via notifier.send_discord_message().
    If both are healthy, sends no alert.

    :param filepath: Path to last_success.json (defaults to config.LAST_SUCCESS_PATH)
    :param now: Optional override for current datetime (used in unit testing)
    :param send_discord: If True, dispatches alert via notifier.send_discord_message on failure
    :param bot_token: Discord Bot Token override
    :param channel_id: Discord Channel ID override
    :return: Dictionary containing check status and alert output
    """
    target_path = filepath if filepath is not None else getattr(config, "LAST_SUCCESS_PATH", None)
    if not target_path:
        target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_success.json")

    data: Dict[str, Any] = {}
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        data = parsed
        except Exception as e:
            logger.warning("Error reading timestamp file %s: %s", target_path, e)
            data = {}

    stale_components: List[str] = []
    messages: List[str] = []
    statuses: Dict[str, Dict[str, Any]] = {}

    for component, max_hours in COMPONENTS_THRESHOLDS.items():
        max_seconds = max_hours * 3600.0
        ts_str = data.get(component)
        dt = parse_iso_timestamp(ts_str) if ts_str else None

        if dt is None:
            stale_components.append(component)
            msg = f"Component **{component}** has gone silent (missing timestamp in last_success.json)."
            messages.append(msg)
            statuses[component] = {
                "status": "missing",
                "age_hours": None,
                "max_hours": max_hours,
            }
        else:
            age_seconds = get_timestamp_age_seconds(dt, now=now)
            age_hours = age_seconds / 3600.0
            is_stale = age_seconds > max_seconds

            statuses[component] = {
                "status": "stale" if is_stale else "ok",
                "age_hours": round(age_hours, 2),
                "max_hours": max_hours,
            }

            if is_stale:
                stale_components.append(component)
                msg = (
                    f"Component **{component}** has gone silent for {age_hours:.1f} hours "
                    f"(threshold: {max_hours:.1f} hours)."
                )
                messages.append(msg)

    alert_sent = False
    alert_text = ""

    if stale_components:
        alert_text = "🚨 **Heartbeat Check Alert - Silent Component(s) Detected**\n" + "\n".join(messages)
        logger.warning("Heartbeat check failed: %s", alert_text)
        if send_discord:
            alert_sent = notifier.send_discord_message(
                content=alert_text,
                bot_token=bot_token,
                channel_id=channel_id,
            )
    else:
        logger.info("Heartbeat check passed: all components healthy.")

    return {
        "healthy": len(stale_components) == 0,
        "stale_components": stale_components,
        "statuses": statuses,
        "alert_sent": alert_sent,
        "alert_text": alert_text,
    }


def register_task_scheduler() -> bool:
    """
    Registers or updates the Task Scheduler entry for heartbeat_check.py to run hourly.
    """
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)
    task_name = "ResearchScanner_HeartbeatCheck"

    cmd = [
        "schtasks",
        "/create",
        "/tn",
        task_name,
        "/tr",
        f'"{python_exe}" "{script_path}"',
        "/sc",
        "hourly",
        "/mo",
        "1",
        "/f",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Successfully registered Task Scheduler task '%s'.", task_name)
            return True
        else:
            logger.error("Failed to register Task Scheduler task '%s': %s", task_name, result.stderr or result.stdout)
            return False
    except Exception as e:
        logger.error("Exception registering Task Scheduler task: %s", e)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Heartbeat check monitor for research_scanner.")
    parser.add_argument("--register", action="store_true", help="Register Task Scheduler job and exit.")
    parser.add_argument("--file", type=str, default=None, help="Path to last_success.json override.")
    args = parser.parse_args()

    if args.register:
        success = register_task_scheduler()
        sys.exit(0 if success else 1)
    else:
        result = check_heartbeat(filepath=args.file)
        if not result["healthy"]:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
