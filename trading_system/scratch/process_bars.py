import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv('/home/mason/Trading/.env')

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
client = StockHistoricalDataClient(api_key, secret_key)

# Read filings
file_path = '/home/mason/Trading/small_cap_robotics_sec_filings.md'
with open(file_path, 'r') as f:
    lines = f.readlines()

filings = []
for line in lines:
    if line.startswith('|') and not 'Ticker' in line and not '|---|' in line:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 5:
            ticker = parts[0]
            company = parts[1]
            filing_type = parts[3]
            filing_date_str = parts[4]
            filings.append({
                'ticker': ticker,
                'company': company,
                'filing_type': filing_type,
                'filing_date': filing_date_str
            })

tickers = list(set([f['ticker'] for f in filings]))

# Fetch daily bars from Alpaca (from 2026-03-01 to 2026-07-24)
req = StockBarsRequest(
    symbol_or_symbols=tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2026, 3, 1),
    end=datetime(2026, 7, 24),
    feed=DataFeed.IEX
)

bars_df = client.get_stock_bars(req).df.reset_index()
bars_df['date'] = pd.to_datetime(bars_df['timestamp']).dt.tz_localize(None).dt.normalize()

results = []
insufficient_data = []

for idx, f in enumerate(filings):
    ticker = f['ticker']
    f_date = pd.to_datetime(f['filing_date']).normalize()
    
    t_bars = bars_df[bars_df['symbol'] == ticker].sort_values('date').reset_index(drop=True)
    
    # Find matching index for filing date t_0
    t0_matches = t_bars[t_bars['date'] == f_date]
    if t0_matches.empty:
        # If filing date is not in trading bars
        insufficient_data.append((idx+1, ticker, f['filing_date'], "Filing date not in trading bars"))
        continue
    
    t0_idx = t0_matches.index[0]
    
    # Check if we have 10 days before and 15 days after
    if t0_idx < 10:
        insufficient_data.append((idx+1, ticker, f['filing_date'], f"Fewer than 10 trading days before (only {t0_idx} days available)"))
        continue
        
    if t0_idx + 15 >= len(t_bars):
        avail_after = len(t_bars) - 1 - t0_idx
        insufficient_data.append((idx+1, ticker, f['filing_date'], f"Fewer than 15 trading days after (only {avail_after} days available as of current date)"))
        continue
        
    # We have sufficient data
    bar_m10_to_m1 = t_bars.iloc[t0_idx-10:t0_idx]
    bar_m1 = t_bars.iloc[t0_idx-1]
    bar_0 = t_bars.iloc[t0_idx]
    bar_p1 = t_bars.iloc[t0_idx+1]
    bar_p5 = t_bars.iloc[t0_idx+5]
    bar_p15 = t_bars.iloc[t0_idx+15]
    bar_p1_to_p15 = t_bars.iloc[t0_idx+1:t0_idx+16]
    
    p_m1 = float(bar_m1['close'])
    p_0 = float(bar_0['close'])
    p_p1 = float(bar_p1['close'])
    p_p5 = float(bar_p5['close'])
    p_p15 = float(bar_p15['close'])
    
    avg_vol_before = float(bar_m10_to_m1['volume'].mean())
    avg_vol_after = float(bar_p1_to_p15['volume'].mean())
    vol_ratio = avg_vol_after / avg_vol_before if avg_vol_before > 0 else 0.0
    
    results.append({
        'row_id': idx + 1,
        'ticker': ticker,
        'filing_date': f['filing_date'],
        'p_m1': p_m1,
        'p_0': p_0,
        'p_p1': p_p1,
        'p_p5': p_p5,
        'p_p15': p_p15,
        'avg_vol_before': avg_vol_before,
        'avg_vol_after': avg_vol_after,
        'vol_ratio': vol_ratio
    })

res_df = pd.DataFrame(results)
print(f"Successfully processed {len(res_df)} rows out of {len(filings)}.")
print(f"Insufficient data rows: {len(insufficient_data)}")
for item in insufficient_data:
    print(item)

print("\nSample processed rows:")
print(res_df.head(10).to_string())
