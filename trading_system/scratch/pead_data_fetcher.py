import os
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv()

def fetch_alpaca_bars_for_universe(universe_path, out_path, min_adv=10000):
    with open(universe_path, 'r') as f:
        universe = json.load(f)

    tickers = [item['ticker'] for item in universe]
    print(f"Loaded {len(tickers)} tickers from universe file.")

    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    client = StockHistoricalDataClient(api_key, secret_key)

    start_dt = datetime(2023, 1, 1)
    end_dt = datetime(2026, 7, 27)

    all_bars_list = []
    chunk_size = 50

    print(f"Fetching Alpaca historical daily bars for {len(tickers)} symbols from {start_dt.date()} to {end_dt.date()}...")
    
    for i in range(0, len(tickers), chunk_size):
        chunk_symbols = tickers[i:i+chunk_size]
        print(f"Fetching chunk {i//chunk_size + 1}/{(len(tickers)+chunk_size-1)//chunk_size} ({len(chunk_symbols)} symbols)...")
        
        req = StockBarsRequest(
            symbol_or_symbols=chunk_symbols,
            timeframe=TimeFrame.Day,
            start=start_dt,
            end=end_dt,
            feed=DataFeed.IEX
        )
        
        try:
            bars_df = client.get_stock_bars(req).df
            if not bars_df.empty:
                all_bars_list.append(bars_df)
        except Exception as e:
            print(f"Error fetching chunk {chunk_symbols[:3]}...: {e}")
        time.sleep(0.3)

    if not all_bars_list:
        print("Error: No bar data retrieved from Alpaca.")
        return None

    full_df = pd.concat(all_bars_list)
    # Re-index / flatten multi-index if needed
    if isinstance(full_df.index, pd.MultiIndex):
        full_df = full_df.reset_index()

    print(f"Total bar records fetched: {len(full_df)}")

    # Standardize column names
    full_df.rename(columns={'symbol': 'ticker', 'timestamp': 'date', 'close': 'close', 'volume': 'volume'}, inplace=True)
    full_df['date'] = pd.to_datetime(full_df['date']).dt.tz_localize(None).dt.floor('D')

    # Apply Liquidity Floor: compute average daily volume per ticker
    adv_series = full_df.groupby('ticker')['volume'].mean()
    liquid_tickers = adv_series[adv_series >= min_adv].index.tolist()
    excluded_tickers = adv_series[adv_series < min_adv].index.tolist()

    print(f"\n--- Liquidity Floor Filter (>= {min_adv:,} shares/day) ---")
    print(f"Qualifying liquid tickers: {len(liquid_tickers)}")
    print(f"Excluded illiquid tickers (< {min_adv:,} shares/day): {len(excluded_tickers)} -> {excluded_tickers[:10]}")

    filtered_df = full_df[full_df['ticker'].isin(liquid_tickers)].copy()
    
    # Save to CSV / Parquet
    filtered_df.to_csv(out_path, index=False)
    print(f"Saved market bar data to {out_path}")

    # Also return summary of liquid universe
    liquid_universe = [item for item in universe if item['ticker'] in liquid_tickers]
    with open('/home/mason/Trading/scratch/pead_liquid_universe.json', 'w') as f:
        json.dump(liquid_universe, f, indent=2)

    return liquid_universe

if __name__ == '__main__':
    fetch_alpaca_bars_for_universe(
        '/home/mason/Trading/scratch/pead_universe.json',
        '/home/mason/Trading/scratch/pead_market_data.csv',
        min_adv=10000
    )
