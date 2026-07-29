import os
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv('/home/mason/Trading/.env')

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
client = StockHistoricalDataClient(api_key, secret_key)

# Read filings table from small_cap_robotics_sec_filings.md
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

req = StockBarsRequest(
    symbol_or_symbols=tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2026, 3, 1),
    end=datetime(2026, 7, 24),
    feed=DataFeed.IEX
)

bars_df = client.get_stock_bars(req).df.reset_index()
bars_df['date'] = pd.to_datetime(bars_df['timestamp']).dt.tz_localize(None).dt.normalize()

table_rows = []
insufficient_rows = []

for idx, f in enumerate(filings):
    ticker = f['ticker']
    f_date = pd.to_datetime(f['filing_date']).normalize()
    
    t_bars = bars_df[bars_df['symbol'] == ticker].sort_values('date').reset_index(drop=True)
    
    t0_matches = t_bars[t_bars['date'] == f_date]
    if t0_matches.empty:
        insufficient_rows.append({
            'row_id': idx + 1,
            'ticker': ticker,
            'filing_date': f['filing_date'],
            'reason': "Filing date not found in market trading bars"
        })
        continue
    
    t0_idx = t0_matches.index[0]
    
    if t0_idx < 10:
        insufficient_rows.append({
            'row_id': idx + 1,
            'ticker': ticker,
            'filing_date': f['filing_date'],
            'reason': f"Fewer than 10 trading days before filing date (only {t0_idx} trading days available)"
        })
        continue
        
    if t0_idx + 15 >= len(t_bars):
        avail_after = len(t_bars) - 1 - t0_idx
        insufficient_rows.append({
            'row_id': idx + 1,
            'ticker': ticker,
            'filing_date': f['filing_date'],
            'reason': f"Fewer than 15 trading days after filing date as of 2026-07-23 (only {avail_after} trading days available)"
        })
        continue
        
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
    
    pct_total = (p_p15 - p_m1) / p_m1 * 100.0
    pct_day1 = (p_p1 - p_m1) / p_m1 * 100.0
    pct_drift = (p_p15 - p_p1) / p_m1 * 100.0
    
    abs_tot = abs(pct_total)
    abs_d1 = abs(pct_day1)
    frac_day1 = pct_day1 / pct_total if pct_total != 0 else 0
    
    if abs_tot < 4.0:
        classification = "FLAT/NONE"
    elif (frac_day1 >= 0.60 and abs(pct_drift) <= max(3.5, 0.4 * abs_d1)) or (abs_d1 >= 10.0 and frac_day1 >= 0.50 and abs(pct_drift) <= 0.5 * abs_d1):
        classification = "INSTANT"
    else:
        classification = "GRADUAL"
        
    flagged = (vol_ratio > 2.0) and (classification == "GRADUAL")
    
    table_rows.append({
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
        'vol_ratio': vol_ratio,
        'classification': classification,
        'flagged': flagged
    })

df_table = pd.DataFrame(table_rows)

print(f"Total Filing Rows: {len(filings)}")
print(f"Successfully Analyzed: {len(df_table)}")
print(f"Insufficient Data Rows: {len(insufficient_rows)}")
print(f"GRADUAL Count: {(df_table['classification'] == 'GRADUAL').sum()}")
print(f"INSTANT Count: {(df_table['classification'] == 'INSTANT').sum()}")
print(f"FLAT/NONE Count: {(df_table['classification'] == 'FLAT/NONE').sum()}")
print(f"Flagged Count: {df_table['flagged'].sum()}")

print("\n--- Insufficient Data Tickers / Dates ---")
for r in insufficient_rows:
    print(f"Row {r['row_id']:2d} | {r['ticker']} | {r['filing_date']} | Reason: {r['reason']}")
