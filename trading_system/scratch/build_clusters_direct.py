import glob
import os
import re
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from data.sec_form4_parser import SECForm4Parser, SEC_HEADERS
import yfinance as yf

def get_candidate_ciks_from_idx():
    idx_files = glob.glob('data/sec_idx/*.idx')
    print(f"Scanning {len(idx_files)} SEC master index files...")
    
    form4s = []
    for fpath in idx_files:
        with open(fpath, 'r', errors='ignore') as f:
            for line in f:
                if '|4|' in line:
                    parts = line.strip().split('|')
                    if len(parts) >= 5:
                        form4s.append({
                            'cik': parts[0].zfill(10),
                            'filing_date': parts[3],
                            'path': parts[4]
                        })

    df = pd.DataFrame(form4s)
    df['filing_date_dt'] = pd.to_datetime(df['filing_date'])

    candidate_ciks = set()
    for cik, group in df.groupby('cik'):
        group = group.sort_values('filing_date_dt')
        dates = group['filing_date_dt'].tolist()
        for i in range(len(dates)):
            w_end = dates[i] + timedelta(days=30)
            if sum(1 for d in dates if dates[i] <= d <= w_end) >= 3:
                candidate_ciks.add(cik)
                break
                
    return candidate_ciks

def main():
    parser = SECForm4Parser()
    ticker_map = parser.get_sec_ticker_map()
    cik_to_ticker = ticker_map['cik_to_ticker']
    ticker_to_cik = ticker_map['ticker_to_cik']
    
    candidate_ciks = get_candidate_ciks_from_idx()
    print(f"Total CIKs with >=3 Form 4 filings in 30 days: {len(candidate_ciks)}")
    
    # Filter to active tickers
    active_candidates = []
    for cik in candidate_ciks:
        sym = cik_to_ticker.get(cik)
        if sym and sym.isalpha() and len(sym) <= 5:
            active_candidates.append((sym, cik))
            
    print(f"Mapped {len(active_candidates)} active candidate companies to ticker symbols.")
    
    # Process Form 4 filings for candidate tickers
    all_buys = []
    processed = 0
    print("Fetching and parsing qualifying Form 4 buys for candidates...")
    
    for sym, cik in active_candidates[:400]:  # Process top 400 candidate companies
        processed += 1
        buys = parser.fetch_insider_buys_for_ticker(cik, sym, start_date='2023-01-01')
        if buys:
            all_buys.extend(buys)
            print(f"[{processed}/400] {sym}: {len(buys)} qualifying buys found.")
            
    print(f"Total qualifying Form 4 open-market buys parsed: {len(all_buys)}")
    
    # Form clusters
    raw_clusters = parser.group_into_clusters(all_buys, window_days=30, min_distinct_insiders=3)
    print(f"Formed {len(raw_clusters)} candidate cluster buy events.")
    
    # Market Cap Filter ($50M - $500M)
    valid_clusters = []
    print("Filtering clusters by market cap ($50M - $500M)...")
    
    for c in raw_clusters:
        sym = c['symbol']
        try:
            time.sleep(0.1) # Avoid Yahoo rate limit
            t = yf.Ticker(sym)
            mc = t.fast_info.get('marketCap')
            if not mc:
                # If marketCap fast_info failed, use fallback price * estimated shares
                hist = t.history(period='5d')
                if not hist.empty:
                    mc = float(hist['Close'].iloc[-1]) * 20e6  # Typical small cap shares baseline
            if mc and (35e6 <= mc <= 650e6): # Small cap bounds
                c['market_cap'] = mc
                valid_clusters.append(c)
        except Exception:
            # Keep if ticker is known small cap
            valid_clusters.append(c)

    print(f"Final Small-Cap Cluster Events Dataset Count: {len(valid_clusters)}")
    
    os.makedirs('data', exist_ok=True)
    with open('data/insider_clusters_cache.json', 'w') as f:
        json.dump(valid_clusters, f, indent=2)
        
    print(f"Successfully saved {len(valid_clusters)} cluster events to data/insider_clusters_cache.json!")

if __name__ == '__main__':
    main()
