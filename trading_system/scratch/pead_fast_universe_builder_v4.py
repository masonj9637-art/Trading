import os
import json
import time
import random
import urllib.request
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

HEADERS = {'User-Agent': 'MasonInvestments mason@example.com'}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def is_common_stock(ticker):
    if not ticker or not ticker.isalpha():
        return False
    if len(ticker) > 5:
        return False
    return True

def process_single_ticker(item):
    ticker = item['ticker']
    if not is_common_stock(ticker):
        return None

    cik_str = item['cik_str']
    cik = str(cik_str).zfill(10)

    # 1. SEC Submissions Check
    sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    sub = fetch_json(sub_url)
    if not sub or 'filings' not in sub:
        return None

    recent = sub['filings'].get('recent', {})
    forms = recent.get('form', [])
    items_list = recent.get('items', [])
    dates = recent.get('filingDate', [])
    acc_times = recent.get('acceptanceDateTime', [])
    accessions = recent.get('accessionNumber', [])

    filings_202 = []
    for i in range(len(forms)):
        form = forms[i]
        fdate = dates[i] if i < len(dates) else ""
        items = items_list[i] if i < len(items_list) else ""
        acc_time = acc_times[i] if i < len(acc_times) else ""
        acc_num = accessions[i] if i < len(accessions) else ""

        if form in ['8-K', '8-K/A'] and '2023-07-01' <= fdate <= '2026-07-27':
            if '2.02' in str(items):
                filings_202.append({
                    'filing_date': fdate,
                    'acceptance_time': acc_time,
                    'items': str(items),
                    'accession': acc_num
                })

    if len(filings_202) < 2:
        return None

    # 2. Market Cap Check
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is not None:
            mc_m = mc / 1e6
            if 50.0 <= mc_m <= 500.0:
                return {
                    'ticker': ticker,
                    'cik': cik,
                    'title': item.get('title', ''),
                    'market_cap_m': mc_m,
                    'filings_count': len(filings_202),
                    'filings': filings_202
                }
    except Exception:
        pass

    return None

def main():
    print("Fetching SEC tickers list...")
    tickers_data = fetch_json('https://www.sec.gov/files/company_tickers.json')
    if not tickers_data:
        print("Failed to fetch SEC tickers.")
        return

    tickers_list = [t for t in tickers_data.values() if is_common_stock(t['ticker'])]
    print(f"Total valid common stock SEC tickers: {len(tickers_list)}")

    random.seed(999)
    random.shuffle(tickers_list)

    qualifying_universe = []
    target_count = 110 # Require at least 100 qualifying small-cap tickers
    batch_size = 5

    print("Screening small-cap ($50M-$500M) companies with Item 2.02 8-K filings in parallel...")
    start_time = time.time()

    for idx in range(0, len(tickers_list), batch_size):
        chunk = tickers_list[idx:idx + batch_size]
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_single_ticker, item) for item in chunk]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    qualifying_universe.append(res)
                    print(f"[{len(qualifying_universe)}/{target_count}] Found {res['ticker']}: Market Cap ${res['market_cap_m']:.1f}M, {res['filings_count']} Item 2.02 8-Ks")
                    if len(qualifying_universe) >= target_count:
                        break

        if len(qualifying_universe) >= target_count:
            break

        time.sleep(0.55) # Keep strictly under 10 req/sec rate limit

    elapsed = time.time() - start_time
    print(f"\nSuccessfully built universe of {len(qualifying_universe)} qualifying tickers in {elapsed:.1f}s.")

    out_file = '/home/mason/Trading/scratch/pead_universe.json'
    with open(out_file, 'w') as f:
        json.dump(qualifying_universe, f, indent=2)
    print(f"Saved universe to {out_file}")

if __name__ == '__main__':
    main()
