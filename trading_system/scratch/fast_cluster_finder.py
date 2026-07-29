import os
import requests
import json
import re
import time
import concurrent.futures
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

SEC_HEADERS = {'User-Agent': 'QuantResearch research@tradingbot.com'}

def download_master_indexes(start_year=2023, end_year=2026, cache_dir='data/sec_idx'):
    os.makedirs(cache_dir, exist_ok=True)
    all_form4s = []
    
    quarters = []
    for y in range(start_year, end_year + 1):
        for q in range(1, 5):
            if y == 2026 and q > 2:
                continue
            quarters.append((y, q))

    print(f"Checking/Downloading SEC master index files for {len(quarters)} quarters...")
    for y, q in quarters:
        idx_path = os.path.join(cache_dir, f'master_{y}_q{q}.idx')
        if not os.path.exists(idx_path):
            url = f'https://www.sec.gov/Archives/edgar/full-index/{y}/QTR{q}/master.idx'
            try:
                r = requests.get(url, headers=SEC_HEADERS, timeout=15)
                if r.status_code == 200:
                    with open(idx_path, 'w') as f:
                        f.write(r.text)
                    print(f"Downloaded master index {y} QTR{q}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Failed {y} QTR{q}: {e}")
                
        if os.path.exists(idx_path):
            with open(idx_path) as f:
                for line in f:
                    if '|4|' in line:
                        parts = line.strip().split('|')
                        if len(parts) >= 5:
                            all_form4s.append({
                                'cik': parts[0].zfill(10),
                                'company': parts[1],
                                'form': parts[2],
                                'filing_date': parts[3],
                                'path': parts[4]
                            })
                            
    print(f"Total Form 4 filing index records extracted across 2023-2026: {len(all_form4s)}")
    return pd.DataFrame(all_form4s)

def find_candidate_ciks(df_form4s, window_days=30, min_filings=3):
    print("Finding CIKs with cluster filing patterns (>=3 Form 4s within 30 days)...")
    df_form4s['filing_date_dt'] = pd.to_datetime(df_form4s['filing_date'])
    candidate_ciks = set()
    
    for cik, group in df_form4s.groupby('cik'):
        group = group.sort_values('filing_date_dt')
        dates = group['filing_date_dt'].tolist()
        for i in range(len(dates)):
            w_end = dates[i] + timedelta(days=window_days)
            count_in_w = sum(1 for d in dates if dates[i] <= d <= w_end)
            if count_in_w >= min_filings:
                candidate_ciks.add(cik)
                break
                
    print(f"Identified {len(candidate_ciks)} CIKs with potential Form 4 cluster activity.")
    return list(candidate_ciks)

def main():
    from data.sec_form4_parser import SECForm4Parser
    parser = SECForm4Parser()
    ticker_map = parser.get_sec_ticker_map()
    cik_to_ticker = ticker_map['cik_to_ticker']
    ticker_to_cik = ticker_map['ticker_to_cik']
    
    df_form4s = download_master_indexes(2023, 2026)
    candidate_ciks = find_candidate_ciks(df_form4s)
    
    # Map candidate CIKs to valid tickers
    candidate_tickers = {}
    for cik in candidate_ciks:
        sym = cik_to_ticker.get(cik)
        if sym and sym.isalpha() and len(sym) <= 5:
            candidate_tickers[sym] = cik
            
    print(f"Mapped {len(candidate_tickers)} candidate CIKs to active ticker symbols.")
    
    # Check Market Cap for candidates ($50M - $500M)
    print("Filtering small-cap universe ($50M-$500M market cap)...")
    small_cap_candidates = {}
    
    def check_mcap(item):
        sym, cik = item
        try:
            t = yf.Ticker(sym)
            mc = t.fast_info.get('marketCap')
            if mc and 40e6 <= mc <= 650e6:  # Slightly broader range to capture historical small caps
                return (sym, cik, mc)
        except Exception:
            pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(check_mcap, item) for item in candidate_tickers.items()]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                sym, cik, mc = res
                small_cap_candidates[sym] = cik

    print(f"Retained {len(small_cap_candidates)} small-cap tickers with cluster Form 4 activity.")
    
    # Process Form 4 XML filings for retained small cap tickers
    print("Fetching and parsing qualifying Form 4 buys for small caps...")
    all_buys = []
    processed = 0
    for sym, cik in small_cap_candidates.items():
        processed += 1
        buys = parser.fetch_insider_buys_for_ticker(cik, sym, start_date='2023-01-01')
        if buys:
            all_buys.extend(buys)
            print(f"[{processed}/{len(small_cap_candidates)}] {sym}: {len(buys)} qualifying buys")
            
    print(f"Total qualifying insider buys parsed: {len(all_buys)}")
    with open('data/insider_buys_cache.json', 'w') as f:
        json.dump(all_buys, f, indent=2)

    clusters = parser.group_into_clusters(all_buys, window_days=30, min_distinct_insiders=3)
    print(f"=== CLUSTER DISCOVERY COMPLETE ===")
    print(f"Total Form 4 cluster events identified: {len(clusters)}")
    
    with open('data/insider_clusters_cache.json', 'w') as f:
        json.dump(clusters, f, indent=2)

if __name__ == '__main__':
    main()
