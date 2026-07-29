import os
import json
import time
import concurrent.futures
import pandas as pd
import yfinance as yf
from data.sec_form4_parser import SECForm4Parser, SEC_HEADERS

def main():
    parser = SECForm4Parser()
    ticker_map = parser.get_sec_ticker_map()['ticker_to_cik']
    
    # Load candidate tickers
    small_cap_file = 'data/small_cap_tickers.json'
    if os.path.exists(small_cap_file):
        with open(small_cap_file, 'r') as f:
            small_cap_data = json.load(f)
        tickers = [item['ticker'] for item in small_cap_data]
    else:
        # Fallback: scan SEC ticker list
        candidates = [t for t in ticker_map.keys() if t.isalpha() and 2 <= len(t) <= 5]
        print(f"Filtering small caps from {len(candidates)} SEC tickers...")
        small_cap_data = parser.get_small_cap_universe(min_mcap=50e6, max_mcap=500e6, max_tickers=1200)
        tickers = [item['ticker'] for item in small_cap_data]

    print(f"Processing Form 4 filings for {len(tickers)} small-cap tickers...")
    
    all_buys = []
    processed_count = 0
    
    def process_symbol(sym):
        cik = ticker_map.get(sym)
        if not cik:
            return []
        try:
            return parser.fetch_insider_buys_for_ticker(cik, sym, start_date='2023-01-01')
        except Exception as e:
            return []

    # Run in parallel with worker pool of 5 to strictly respect SEC 10 req/sec rate limit
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_symbol, sym): sym for sym in tickers}
        for future in concurrent.futures.as_completed(futures):
            sym = futures[future]
            processed_count += 1
            buys = future.result()
            if buys:
                all_buys.extend(buys)
                print(f"[{processed_count}/{len(tickers)}] {sym}: {len(buys)} qualifying buys")
            if processed_count % 50 == 0:
                print(f"Progress: {processed_count}/{len(tickers)} tickers processed. Total buys so far: {len(all_buys)}")

    print(f"Total qualifying insider buys extracted across universe: {len(all_buys)}")
    
    # Save raw buys cache
    with open('data/insider_buys_cache.json', 'w') as f:
        json.dump(all_buys, f, indent=2)
        
    clusters = parser.group_into_clusters(all_buys, window_days=30, min_distinct_insiders=3)
    print(f"Total cluster buy events identified: {len(clusters)}")
    
    with open('data/insider_clusters_cache.json', 'w') as f:
        json.dump(clusters, f, indent=2)
        
    print(f"Saved {len(clusters)} clusters to data/insider_clusters_cache.json")

if __name__ == '__main__':
    main()
