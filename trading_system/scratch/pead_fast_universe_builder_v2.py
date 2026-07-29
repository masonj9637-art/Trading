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

def check_sec_filings(item):
    ticker = item['ticker']
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

    tickers_list = list(tickers_data.values())
    print(f"Total SEC tickers: {len(tickers_list)}")

    random.seed(42)
    random.shuffle(tickers_list)

    sec_candidates = []
    target_count = 115 # Need at least 100 qualifying small-cap tickers
    batch_size = 5

    print("Phase 1: Screening SEC for companies with >= 2 Item 2.02 8-Ks...")
    start_time = time.time()
    
    for idx in range(0, len(tickers_list), batch_size):
        chunk = tickers_list[idx:idx + batch_size]
        for item in chunk:
            res = check_sec_filings(item)
            time.sleep(0.11) # SEC rate limit compliance (<10 req/sec)
            if res:
                sec_candidates.append(res)
                print(f"SEC Candidate {len(sec_candidates)}: {res['ticker']} ({res['filings_count']} Item 2.02 filings)")

        # Evaluate market caps in parallel every time we accumulate 15 SEC candidates
        if len(sec_candidates) >= 15:
            qualifying = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_mcap, c) for c in sec_candidates]
                for future in as_completed(futures):
                    r = future.result()
                    if r:
                        qualifying.append(r)
            
            print(f"--> Checked market caps: {len(qualifying)} / {len(sec_candidates)} meet $50M-$500M market cap.")
            if len(qualifying) >= target_count:
                sec_candidates = qualifying[:target_count]
                break

    # Final pass on market caps
    print(f"\nPhase 2: Final market cap verification on {len(sec_candidates)} candidates...")
    final_universe = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(get_mcap, c) for c in sec_candidates]
        for future in as_completed(futures):
            r = future.result()
            if r:
                final_universe.append(r)
                print(f"Qualifying Universe #{len(final_universe)}: {r['ticker']} (${r['market_cap_m']:.1f}M, {r['filings_count']} filings)")

    elapsed = time.time() - start_time
    print(f"\nSuccessfully built universe of {len(final_universe)} qualifying tickers in {elapsed:.1f}s.")

    out_file = '/home/mason/Trading/scratch/pead_universe.json'
    with open(out_file, 'w') as f:
        json.dump(final_universe, f, indent=2)
    print(f"Saved universe to {out_file}")

if __name__ == '__main__':
    main()
