import os
import json
import time
import random
import urllib.request
import pandas as pd
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

NASDAQ_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
SEC_HEADERS = {'User-Agent': 'MasonInvestments mason@example.com'}

def fetch_json(url, headers=SEC_HEADERS):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def is_common_stock(ticker, name=""):
    if not ticker or not ticker.isalpha():
        return False
    if len(ticker) > 5:
        return False
    name_upper = name.upper()
    exclude_keywords = ['FUND', 'TRUST', 'ETF', 'PREFERRED', 'INDEX', 'BENEFICIAL', 'RIGHTS', 'WARRANT']
    if any(k in name_upper for k in exclude_keywords):
        return False
    return True

def process_sec_smallcap(item):
    ticker = item['ticker']
    cik = str(item['cik']).zfill(10)

    sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    sub = fetch_json(sub_url, headers=SEC_HEADERS)
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
            'title': item.get('name', ''),
            'market_cap_m': item['market_cap_m'],
            'filings_count': len(filings_202),
            'filings': filings_202
        }
    return None

def main():
    print("Step 1: Fetching verified small-cap ($50M-$500M) stocks from NASDAQ screener API...")
    url = 'https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000'
    screener_data = fetch_json(url, headers=NASDAQ_HEADERS)
    if not screener_data or 'data' not in screener_data or 'table' not in screener_data['data']:
        print("Failed to fetch NASDAQ screener data.")
        return

    rows = screener_data['data']['table']['rows']
    print(f"Total US stocks returned: {len(rows)}")

    small_cap_map = {}
    for r in rows:
        sym = r['symbol']
        name = r.get('name', '')
        if not is_common_stock(sym, name):
            continue
        mc_str = r.get('marketCap', '').replace(',', '').strip()
        if mc_str.isdigit():
            mc_val = float(mc_str)
            mc_m = mc_val / 1e6
            if 50.0 <= mc_m <= 500.0:
                small_cap_map[sym] = {'ticker': sym, 'name': name, 'market_cap_m': mc_m}

    print(f"Found {len(small_cap_map)} verified small-cap ($50M-$500M) common stocks.")

    print("Step 2: Mapping SEC CIKs...")
    sec_tickers = fetch_json('https://www.sec.gov/files/company_tickers.json', headers=SEC_HEADERS)
    if not sec_tickers:
        print("Failed to fetch SEC tickers map.")
        return

    ticker_to_cik = {}
    for item in sec_tickers.values():
        t = item['ticker']
        if t in small_cap_map:
            small_cap_map[t]['cik'] = item['cik_str']
            ticker_to_cik[t] = small_cap_map[t]

    candidates_list = list(ticker_to_cik.values())
    print(f"Mapped {len(candidates_list)} small-cap tickers with valid SEC CIKs.")

    random.seed(42)
    random.shuffle(candidates_list)

    print("Step 3: Screening SEC EDGAR for 8-K Item 2.02 earnings filings...")
    start_time = time.time()

    qualifying_universe = []
    target_count = 300 # Screen 300 small-cap tickers to ensure >100 liquid tickers after 10k ADV floor
    batch_size = 6

    for idx in range(0, len(candidates_list), batch_size):
        chunk = candidates_list[idx:idx + batch_size]
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(process_sec_smallcap, item) for item in chunk]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    qualifying_universe.append(res)
                    if len(qualifying_universe) % 15 == 0:
                        print(f"[{len(qualifying_universe)}/{target_count}] Qualifying Universe: {res['ticker']} (${res['market_cap_m']:.1f}M, {res['filings_count']} Item 2.02 8-Ks)")
                    if len(qualifying_universe) >= target_count:
                        break

        if len(qualifying_universe) >= target_count:
            break

        time.sleep(0.55) # Pacing SEC rate limits (<10 req/sec)

    elapsed = time.time() - start_time
    print(f"\nSuccessfully built universe of {len(qualifying_universe)} qualifying small-cap tickers in {elapsed:.1f}s.")

    out_file = '/home/mason/Trading/scratch/pead_universe.json'
    with open(out_file, 'w') as f:
        json.dump(qualifying_universe, f, indent=2)
    print(f"Saved universe to {out_file}")

if __name__ == '__main__':
    main()
