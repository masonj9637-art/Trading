"""
Forward Performance Scoring Engine for research_scanner.

Evaluates thesis ledger entries 20, 60, and 120 trading days after audit_date using Alpaca price data,
applies 10bps round-trip transaction costs, compares against random non-candidate baselines,
dispatches Discord REST notifications, and provides aggregate statistical reporting with an N >= 30 sample size floor.
"""

import argparse
import logging
import random
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import requests
import yfinance as yf

from research_scanner import config
from research_scanner.db import (
    init_db,
    get_all_ledger_entries,
    get_unscored_ledger_entries,
    save_thesis_score,
    get_all_thesis_scores,
)
from research_scanner.notifier import send_discord_notification

logger = logging.getLogger("research_scanner.scoring")

# Supported evaluation horizons (trading days)
EVALUATION_HORIZONS = [20, 60, 120]

# Default pool of baseline tickers for null-hypothesis comparison
BASELINE_TICKER_POOL = [
    "SPY", "QQQ", "IWM", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "JPM", "BAC",
    "XOM", "UNH", "PG", "HD", "COST", "MA", "V", "DIS", "NFLX", "AMD",
]


def add_trading_days(start_date_str: str, trading_days: int) -> str:
    """
    Estimates the exit calendar date corresponding to a given number of trading days.
    (Approx 1 trading day ~= 1.45 calendar days to account for weekends and holidays).
    """
    try:
        start_dt = datetime.strptime(start_date_str[:10], "%Y-%m-%d")
    except ValueError:
        start_dt = datetime.now()

    calendar_days_to_add = int(trading_days * 1.45)
    exit_dt = start_dt + timedelta(days=calendar_days_to_add)
    return exit_dt.strftime("%Y-%m-%d")


def is_horizon_eligible(audit_date_str: str, horizon_days: int) -> bool:
    """
    Checks if enough calendar time has elapsed since audit_date to evaluate the horizon.
    """
    try:
        audit_dt = datetime.strptime(audit_date_str[:10], "%Y-%m-%d")
    except ValueError:
        return False

    now = datetime.now()
    calendar_days_elapsed = (now - audit_dt).days
    min_required_calendar_days = int(horizon_days * 1.4)
    return calendar_days_elapsed >= min_required_calendar_days


def get_alpaca_price(
    ticker: str,
    target_date: str,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    base_url: Optional[str] = None,
    mock: bool = False,
) -> Optional[float]:
    """
    Pulls historical close price for a ticker on or immediately following target_date from Alpaca API.
    Logs an ERROR and returns None if Alpaca credentials are missing or API fails, unless mock=True.
    """
    key = api_key if api_key is not None else config.ALPACA_API_KEY
    sec = secret_key if secret_key is not None else config.ALPACA_SECRET_KEY

    if key and sec:
        headers = {
            "APCA-API-KEY-ID": key,
            "APCA-API-SECRET-KEY": sec,
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars"
        params = {
            "start": target_date,
            "timeframe": "1Day",
            "limit": 5,
        }
        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                bars = data.get("bars", [])
                if bars and len(bars) > 0:
                    return float(bars[0].get("c", 0.0) or bars[0].get("o", 0.0))
            logger.error("Alpaca API call failed for %s on %s: HTTP %s", ticker, target_date, res.status_code)
        except Exception as e:
            logger.error("Alpaca API call failed for %s on %s: %s", ticker, target_date, e)
    else:
        logger.error("Missing Alpaca API credentials. Cannot fetch price for %s on %s.", ticker, target_date)

    if mock:
        seed_str = f"{ticker}:{target_date}"
        rand_val = int(hashlib_seed(seed_str), 16) % 10000
        mock_price = 50.0 + (rand_val / 100.0)
        logger.debug("Using fallback mock price %.2f for %s on %s", mock_price, ticker, target_date)
        return mock_price

    return None


def get_yfinance_price(
    ticker: str,
    target_date: str,
) -> Optional[float]:
    """
    Fetches historical daily close price for ticker on or immediately following target_date using yfinance's Ticker.history().
    Returns None if ticker/date isn't found or call fails for any reason (fails gracefully, never raises uncaught exception).
    """
    try:
        start_dt = datetime.strptime(target_date[:10], "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=7)
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")

        t = yf.Ticker(ticker)
        df = t.history(start=start_str, end=end_str)
        if df is not None and not df.empty and "Close" in df.columns:
            close_val = df["Close"].iloc[0]
            if close_val is not None and not (isinstance(close_val, float) and (close_val != close_val)):
                return float(close_val)
    except Exception as e:
        logger.debug("yfinance price fetch failed for %s on %s: %s", ticker, target_date, e)

    return None


def get_price_with_fallback(
    ticker: str,
    target_date: str,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    base_url: Optional[str] = None,
    mock: bool = False,
) -> Tuple[Optional[float], Optional[str]]:
    """
    Three-tier price fallback mechanism:
    1. Try get_alpaca_price() first.
    2. If Alpaca returns None, log notice and try get_yfinance_price() as fallback.
    3. If BOTH return None, returns (None, None).
    """
    alpaca_price = get_alpaca_price(ticker, target_date, api_key=api_key, secret_key=secret_key, base_url=base_url, mock=mock)
    if alpaca_price is not None:
        return alpaca_price, "alpaca"

    logger.info("Alpaca price unavailable for %s on %s, falling back to yfinance", ticker, target_date)
    yf_price = get_yfinance_price(ticker, target_date)
    if yf_price is not None:
        return yf_price, "yfinance"

    return None, None


def hashlib_seed(val: str) -> str:
    import hashlib
    return hashlib.md5(val.encode("utf-8")).hexdigest()


def calculate_cost_adjusted_return(entry_price: float, exit_price: float, bps: float = config.TRANSACTION_COST_BPS) -> float:
    """
    Calculates cost-adjusted net return applying round-trip transaction costs in basis points (10 bps = 0.0010).
    net_return = (exit_price / entry_price) * (1.0 - (bps / 10000.0)) - 1.0
    """
    if entry_price <= 0:
        return 0.0
    gross_ratio = exit_price / entry_price
    cost_factor = 1.0 - (bps / 10000.0)
    return (gross_ratio * cost_factor) - 1.0


def get_baseline_ticker(db_path: str, audit_date: str, thesis_ticker: str) -> str:
    """
    Pulls a random ticker from the fetched_items table that was fetched around the same time
    but never promoted to a note (cleared Archivist but not Curator's relevance bar).
    """
    import re
    from research_scanner.db import get_db_connection
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, summary FROM fetched_items
            WHERE consumed_by_curator = 0
              AND date(fetched_at) >= date(?, '-14 days')
              AND date(fetched_at) <= date(?, '+14 days')
            """,
            (audit_date[:10], audit_date[:10])
        )
        rows = cursor.fetchall()
        
        possible_tickers = []
        ticker_regex = re.compile(r"\$([A-Z]{1,5})\b")
        for row in rows:
            text = f"{row['title'] or ''} {row['summary'] or ''}"
            possible_tickers.extend(ticker_regex.findall(text))
            
        valid = list(set([t for t in possible_tickers if t != thesis_ticker]))
        if valid:
            return random.choice(valid)
    except Exception as e:
        logger.warning("Failed to pull baseline ticker from fetched_items: %s", e)
    finally:
        conn.close()

    # Fallback if no valid tickers found in the database for that window
    return random.choice([t for t in BASELINE_TICKER_POOL if t != thesis_ticker])


def score_unscored_theses(
    db_path: str = config.DB_PATH,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    mock: bool = False,
) -> Dict[str, int]:
    """
    Checks for thesis_ledger entries eligible for 20, 60, and 120-day evaluation,
    pulls prices, calculates 10bps cost-adjusted returns vs. random baseline,
    saves score records, and dispatches Discord notifications.
    """
    init_db(db_path)
    stats = {"evaluated": 0, "scored": 0, "notifications_sent": 0}

    for horizon in EVALUATION_HORIZONS:
        unscored_entries = get_unscored_ledger_entries(db_path, horizon_days=horizon)
        for entry in unscored_entries:
            ledger_id = entry["id"]
            ticker = entry["ticker"]
            audit_date = entry["audit_date"]

            if not is_horizon_eligible(audit_date, horizon):
                logger.debug("Entry ID %d (%s) not yet eligible for %dD horizon.", ledger_id, ticker, horizon)
                continue

            stats["evaluated"] += 1
            exit_date = add_trading_days(audit_date, horizon)

            # 1. Fetch thesis ticker prices
            entry_price, entry_src = get_price_with_fallback(ticker, audit_date, api_key=api_key, secret_key=secret_key, mock=mock)
            exit_price, exit_src = get_price_with_fallback(ticker, exit_date, api_key=api_key, secret_key=secret_key, mock=mock)

            if not entry_price or not exit_price:
                logger.warning("Could not fetch valid prices for thesis ticker %s. Skipping.", ticker)
                continue

            gross_ret = (exit_price - entry_price) / entry_price
            net_ret = calculate_cost_adjusted_return(entry_price, exit_price)
            price_source = "yfinance" if (entry_src == "yfinance" or exit_src == "yfinance") else "alpaca"

            # 2. Pair with random null-hypothesis baseline ticker from fetched_items (rejected universe)
            baseline_ticker = get_baseline_ticker(db_path, audit_date, ticker)
            b_entry_price, b_entry_src = get_price_with_fallback(baseline_ticker, audit_date, api_key=api_key, secret_key=secret_key, mock=mock)
            b_exit_price, b_exit_src = get_price_with_fallback(baseline_ticker, exit_date, api_key=api_key, secret_key=secret_key, mock=mock)

            if not b_entry_price or not b_exit_price:
                failed_date = audit_date if not b_entry_price else exit_date
                logger.warning("Could not fetch valid baseline price for ticker %s on %s. Skipping.", baseline_ticker, failed_date)
                continue

            baseline_net_ret = calculate_cost_adjusted_return(b_entry_price, b_exit_price)
            baseline_price_source = "yfinance" if (b_entry_src == "yfinance" or b_exit_src == "yfinance") else "alpaca"

            # 3. Save score record
            score_record = {
                "ledger_id": ledger_id,
                "horizon_days": horizon,
                "ticker": ticker,
                "entry_date": audit_date,
                "exit_date": exit_date,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_return": gross_ret,
                "net_return": net_ret,
                "baseline_ticker": baseline_ticker,
                "baseline_net_return": baseline_net_ret,
                "price_source": price_source,
                "baseline_price_source": baseline_price_source,
            }

            saved = save_thesis_score(db_path, score_record)
            if saved:
                stats["scored"] += 1

                # 4. Dispatch Discord Notification
                candidate_alert = {
                    "title": f"Thesis Performance Scored ({horizon}D Horizon)",
                    "score": round((net_ret * 100), 2),
                    "source": "THESIS_LEDGER",
                    "category": entry.get("theme_note", "general"),
                    "url": entry.get("vault_note_path", ""),
                    "reason": (
                        f"Ticker: **{ticker}** | Verdict: **{entry.get('fact_check_verdict')}** | "
                        f"Confidence: **{entry.get('confidence_level')}**\n"
                        f"Net Return ({horizon}D): **{net_ret * 100:+.2f}%** (Cost-Adjusted)\n"
                        f"Baseline ({baseline_ticker}): **{baseline_net_ret * 100:+.2f}%**\n"
                        f"Alpha vs Baseline: **{(net_ret - baseline_net_ret) * 100:+.2f}%**"
                    ),
                }
                notified = send_discord_notification(candidate_alert)
                if notified:
                    stats["notifications_sent"] += 1

    logger.info("Scoring cycle complete. Stats: Evaluated=%d | Scored=%d | Notified=%d", stats["evaluated"], stats["scored"], stats["notifications_sent"])
    return stats


def generate_scoring_report(db_path: str = config.DB_PATH, min_n: int = config.MIN_SAMPLE_SIZE_FLOOR) -> None:
    """
    Prints an aggregate statistical report grouped by confidence_level and fact_check_verdict.
    Explicitly enforces min_n sample size floor (default N >= 30) before stating directional conclusions.
    """
    init_db(db_path)
    all_scores = get_all_thesis_scores(db_path)

    print("\n" + "=" * 90)
    print(f" RESEARCH SCANNER - FORWARD THESIS SCORING REPORT ".center(90, "="))
    print(f" (Min Sample Size Floor: N = {min_n} scored theses per horizon) ".center(90, "="))
    print("=" * 90 + "\n")

    if not all_scores:
        print(" No scored theses available in database yet.\n")
        print("=" * 90 + "\n")
        return

    # Group scores by horizon
    by_horizon: Dict[int, List[Dict[str, Any]]] = {}
    for s in all_scores:
        h = s["horizon_days"]
        by_horizon.setdefault(h, []).append(s)

    for horizon in EVALUATION_HORIZONS:
        scores_h = by_horizon.get(horizon, [])
        n_total = len(scores_h)

        print(f"--- HORIZON: {horizon} Trading Days (Total Sample Size N = {n_total}) ---")

        if n_total < min_n:
            print(
                f"  ⚠️  [UNDERPOWERED STATUS]: Current sample size N = {n_total} is below the required "
                f"minimum floor of N = {min_n}.\n"
                f"      Refusing to state a directional conclusion or claim predictive validity until N >= {min_n}.\n"
            )

        if n_total > 0:
            avg_net_ret = sum(s["net_return"] for s in scores_h) / n_total
            avg_base_ret = sum(s["baseline_net_return"] for s in scores_h) / n_total
            avg_alpha = avg_net_ret - avg_base_ret

            print(f"  Overall Mean Net Return:     {avg_net_ret * 100:+.2f}% (10bps Cost-Adjusted)")
            print(f"  Overall Mean Baseline Return:{avg_base_ret * 100:+.2f}% ({BASELINE_TICKER_POOL[0]} Pool)")
            print(f"  Overall Mean Excess Alpha:  {avg_alpha * 100:+.2f}%\n")

            # Breakdown by Confidence Level
            by_conf: Dict[str, List[Dict[str, Any]]] = {}
            for s in scores_h:
                conf = s.get("confidence_level", "Unknown")
                by_conf.setdefault(conf, []).append(s)

            print("  Breakdown by Stated Confidence Level:")
            for conf, group in by_conf.items():
                n_g = len(group)
                mean_net = sum(g["net_return"] for g in group) / n_g
                mean_base = sum(g["baseline_net_return"] for g in group) / n_g
                status = "VALID" if n_g >= min_n else "UNDERPOWERED"
                print(
                    f"    - Confidence '{conf:<10}': N = {n_g:<3} | Net Ret: {mean_net * 100:+.2f}% | "
                    f"Baseline: {mean_base * 100:+.2f}% | Alpha: {(mean_net - mean_base) * 100:+.2f}% [{status}]"
                )

            # Breakdown by Fact-Check Verdict
            by_verdict: Dict[str, List[Dict[str, Any]]] = {}
            for s in scores_h:
                verdict = s.get("fact_check_verdict", "Unknown")
                by_verdict.setdefault(verdict, []).append(s)

            print("\n  Breakdown by Fact-Check Verdict:")
            for verdict, group in by_verdict.items():
                n_g = len(group)
                mean_net = sum(g["net_return"] for g in group) / n_g
                mean_base = sum(g["baseline_net_return"] for g in group) / n_g
                status = "VALID" if n_g >= min_n else "UNDERPOWERED"
                print(
                    f"    - Verdict    '{verdict:<10}': N = {n_g:<3} | Net Ret: {mean_net * 100:+.2f}% | "
                    f"Baseline: {mean_base * 100:+.2f}% | Alpha: {(mean_net - mean_base) * 100:+.2f}% [{status}]"
                )

        print("-" * 90)

    print("=" * 90 + "\n")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    parser = argparse.ArgumentParser(
        description="Forward Performance Scoring & Statistical Reporting for research_scanner thesis_ledger."
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print aggregate statistical performance report (with N >= 30 sample size floor check)",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=config.DB_PATH,
        help=f"Path to SQLite database (default: {config.DB_PATH})",
    )
    parser.add_argument(
        "--min-n",
        type=int,
        default=config.MIN_SAMPLE_SIZE_FLOOR,
        help=f"Minimum sample size floor for directional conclusions (default: {config.MIN_SAMPLE_SIZE_FLOOR})",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use deterministic mock prices instead of real Alpaca API calls (for testing only)",
    )

    args = parser.parse_args()

    if args.report:
        generate_scoring_report(db_path=args.db, min_n=args.min_n)
    else:
        score_unscored_theses(db_path=args.db, mock=args.mock)


if __name__ == "__main__":
    main()
