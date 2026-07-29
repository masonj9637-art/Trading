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
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def is_common_stock(ticker):
    if not ticker or not ticker.isalpha():
        return False
    if len(ticker) > 5:
        return False
    return True

def get_market_cap_fast(ticker):
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is not None:
            return mc / 1e6
    except Exception:
        pass
    return None

def process_sec_item(item):
    ticker = item['ticker']
    cik = str(item['cik_str']).zfill(10)

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
    for f, itms, d, acc_t, acc_n in zip(forms, items_list, dates, acc_times, accessions):
        if f in ['8-K', '8-K/A'] and '2023-07-01' <= d <= '2026-07-27':
            if '2.02' in str(itms):
                filings_202.append({
                    'filing_date': d,
                    'acceptance_time': acc_t,
                    'items': str(itms),
                    'accession': acc_n
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

def main():
    print("Fetching SEC tickers list...")
    tickers_data = fetch_json('https://www.sec.gov/files/company_tickers.json')
    if not tickers_data:
        print("Failed to fetch SEC tickers.")
        return

    tickers_list = [t for t in tickers_data.values() if is_common_stock(t['ticker'])]
    print(f"Total valid common stock SEC tickers: {len(tickers_list)}")

    random.seed(42)
    random.shuffle(tickers_list)

    sec_candidates = []
    qualifying_universe = []
    target_count = 110 # Require at least 100 qualifying small-cap tickers

    print("Phase 1: Fast SEC EDGAR screening for Item 2.02 filings...")
    start_time = time.time()

    # Step 1: Paced SEC screening using 4 workers
    batch_size = 4
    for idx in range(0, len(tickers_list), batch_size):
        chunk = tickers_list[idx:idx + batch_size]
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_sec_item, item) for item in chunk]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    sec_candidates.append(res)
                    print(f"[{len(sec_candidates)}] SEC Candidate Found: {res['ticker']} ({res['filings_count']} Item 2.02 8-Ks)")
        
        # When we collect 30 SEC candidates, test their market caps in parallel
        if len(sec_candidates) >= 30:
            print(f"\n--- Parallel Market Cap Check on {len(sec_candidates)} SEC Candidates ---")
            
            def check_mcap(cand):
                mc_m = get_market_cap_fast(cand['ticker'])
                if mc_m is not None and (50.0 <= mc_m <= 500.0):
                    cand['market_cap_m'] = mc_m
                    return cand
                return None

            with ThreadPoolExecutor(max_workers=15) as mcap_executor:
                mcap_futures = [mcap_executor.submit(check_mcap, c) for c in sec_candidates]
                for future in as_completed(mcap_futures):
                    r = future.result()
                    if r and r not in qualifying_universe:
                        qualifying_universe.append(r)
                        print(f"  -> Qualifying Universe [{len(qualifying_universe)}/{target_count}]: {r['ticker']} (${r['market_cap_m']:.1f}M, {r['filings_count']} 8-Ks)")

            sec_candidates = [] # Clear evaluated candidates pool

            if len(qualifying_universe) >= target_count:
                break

        time.sleep(0.40)

    # Process any leftover candidates
    if sec_candidates and len(qualifying_universe) < target_count:
        def check_mcap(cand):
            mc_m = get_market_cap_fast(cand['ticker'])
            if mc_m is not None and (50.0 <= mc_m <= 500.0):
                cand['market_cap_m'] = mc_m
                return cand
            return None

        with ThreadPoolExecutor(max_workers=15) as mcap_executor:
            mcap_futures = [mcap_executor.submit(check_mcap, c) for c in sec_candidates]
            for future in as_completed(mcap_futures):
                r = future.result()
                if r and r not in qualifying_universe:
                    qualifying_universe.append(r)
                    print(f"  -> Qualifying Universe [{len(qualifying_universe)}/{target_count}]: {r['ticker']} (${r['market_cap_m']:.1f}M, {r['filings_count']} 8-Ks)")

    elapsed = time.time() - start_time
    print(f"\nSuccessfully built universe of {len(qualifying_universe)} qualifying tickers in {elapsed:.1f}s.")

    out_file = '/home/mason/Trading/scratch/pead_universe.json'
    with open(out_file, 'w') as f:
        json.dump(qualifying_universe, f, indent=2)
    print(f"Saved universe to {out_file}")

if __name__ == '__main__':
    main()
