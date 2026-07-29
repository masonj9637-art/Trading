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
    # Only standard common stock tickers (no preferred shares, warrants, or test symbols)
    if not ticker or not ticker.isalpha():
        return False
    if len(ticker) > 5:
        return False
    return True

def check_sec_filings(item):
    ticker = item['ticker']
    if not is_common_stock(ticker):
        return None

    cik_str = item['cik_str']
    cik = str(cik_str).zfill(10)

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

    if len(filings_202) >= 2:
        return {
            'ticker': ticker,
            'cik': cik,
            'title': item.get('title', ''),
            'filings_count': len(filings_202),
            'filings': filings_202
        }
    return None

def get_mcap(candidate):
    ticker = candidate['ticker']
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is not None:
            mc_m = mc / 1e6
            if 50.0 <= mc_m <= 500.0:
                candidate['market_cap_m'] = mc_m
                return candidate
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

    random.seed(12345)
    random.shuffle(tickers_list)

    qualifying_universe = []
    target_count = 110 # Require at least 100 qualifying small-cap tickers
    
    print("Screening small-cap ($50M-$500M) companies with Item 2.02 8-K filings...")
    start_time = time.time()

    sec_candidates_pool = []
    batch_size = 5

    for idx in range(0, len(tickers_list), batch_size):
        chunk = tickers_list[idx:idx + batch_size]
        for item in chunk:
            res = check_sec_filings(item)
            time.sleep(0.11)
            if res:
                sec_candidates_pool.append(res)
                print(f"SEC Candidate #{len(sec_candidates_pool)}: {res['ticker']} ({res['filings_count']} Item 2.02 filings)")

        # Periodically check market caps for new candidates using ThreadPoolExecutor
        if len(sec_candidates_pool) >= 30:
            print(f"\n--- Checking market caps for {len(sec_candidates_pool)} accumulated candidates ---")
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = [executor.submit(get_mcap, c) for c in sec_candidates_pool]
                for future in as_completed(futures):
                    r = future.result()
                    if r and r not in qualifying_universe:
                        qualifying_universe.append(r)
                        print(f"Qualifying Universe [{len(qualifying_universe)}/{target_count}]: {r['ticker']} (${r['market_cap_m']:.1f}M, {r['filings_count']} filings)")
            
            sec_candidates_pool = [] # Reset pool

            if len(qualifying_universe) >= target_count:
                break

    # Process remaining candidates
    if sec_candidates_pool and len(qualifying_universe) < target_count:
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(get_mcap, c) for c in sec_candidates_pool]
            for future in as_completed(futures):
                r = future.result()
                if r and r not in qualifying_universe:
                    qualifying_universe.append(r)
                    print(f"Qualifying Universe [{len(qualifying_universe)}/{target_count}]: {r['ticker']} (${r['market_cap_m']:.1f}M, {r['filings_count']} filings)")

    elapsed = time.time() - start_time
    print(f"\nSuccessfully built universe of {len(qualifying_universe)} qualifying tickers in {elapsed:.1f}s.")

    out_file = '/home/mason/Trading/scratch/pead_universe.json'
    with open(out_file, 'w') as f:
        json.dump(qualifying_universe, f, indent=2)
    print(f"Saved universe to {out_file}")

if __name__ == '__main__':
    main()
