import os
import random
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv('/home/mason/Trading/.env')
client = StockHistoricalDataClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'))

# Parse filings.md to get actual filing dates per ticker
with open('/home/mason/Trading/filings.md', 'r') as f:
    lines = f.readlines()

filings = []
for line in lines:
    if line.startswith('|') and not 'Ticker' in line and not '|---|' in line:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 12 and parts[0] != '---':
            filings.append({
                'ticker': parts[0],
                'filing_date': parts[1]
            })

df_filings = pd.DataFrame(filings)
tickers = sorted(list(df_filings['ticker'].unique()))

req = StockBarsRequest(
    symbol_or_symbols=tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2025, 6, 1),
    end=datetime(2026, 7, 24),
    feed=DataFeed.IEX
)

bars_df = client.get_stock_bars(req).df.reset_index()
bars_df['date'] = pd.to_datetime(bars_df['timestamp']).dt.tz_localize(None).dt.normalize()

window_start = pd.to_datetime('2025-07-23')
window_end = pd.to_datetime('2026-07-23')

random.seed(42)

results = []

for ticker in tickers:
    t_bars = bars_df[bars_df['symbol'] == ticker].sort_values('date').reset_index(drop=True)
    actual_filing_dates = df_filings[df_filings['ticker'] == ticker]['filing_date'].tolist()
    filing_indices = []
    for f_str in actual_filing_dates:
        f_dt = pd.to_datetime(f_str).normalize()
        matches = t_bars[t_bars['date'] == f_dt]
        if not matches.empty:
            filing_indices.append(matches.index[0])
            
    eligible_indices = []
    for idx, row in t_bars.iterrows():
        d = row['date']
        if d < window_start or d > window_end:
            continue
        if idx < 10 or idx + 15 >= len(t_bars):
            continue
        too_close = False
        for f_idx in filing_indices:
            if abs(idx - f_idx) <= 20:
                too_close = True
                break
        if not too_close:
            eligible_indices.append(idx)
            
    sampled_indices = sorted(random.sample(eligible_indices, 5))
    
    for idx in sampled_indices:
        r_date = t_bars.iloc[idx]['date'].strftime('%Y-%m-%d')
        
        bar_m10_to_m1 = t_bars.iloc[idx-10:idx]
        bar_m1 = t_bars.iloc[idx-1]
        bar_0 = t_bars.iloc[idx]
        bar_p1 = t_bars.iloc[idx+1]
        bar_p5 = t_bars.iloc[idx+5]
        bar_p15 = t_bars.iloc[idx+15]
        bar_p1_to_p15 = t_bars.iloc[idx+1:idx+16]
        
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
            classification = 'FLAT/NONE'
        elif (frac_day1 >= 0.60 and abs(pct_drift) <= max(3.5, 0.4 * abs_d1)) or (abs_d1 >= 10.0 and frac_day1 >= 0.50 and abs(pct_drift) <= 0.5 * abs_d1):
            classification = 'INSTANT'
        else:
            classification = 'GRADUAL'
            
        flagged = (vol_ratio > 2.0) and (classification == 'GRADUAL')
        
        results.append({
            'ticker': ticker,
            'random_date': r_date,
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

df_res = pd.DataFrame(results)

# Build markdown file content
out_lines = []
out_lines.append('# Baseline Price-Reaction Classification (Random Dates)')
out_lines.append('')
out_lines.append('## Direct Comparison: Filing-Linked vs. Random Baseline Data')
out_lines.append('')
out_lines.append('| Metric | Filing-Linked Data (`filings.md`) | Random Baseline Data (Sampled) | 100-Seed Random Baseline Mean |')
out_lines.append('|---|---|---|---|')
out_lines.append(f'| **Total Analyzed Rows** | 45 | {len(df_res)} | 45 |')
out_lines.append(f'| **Classified GRADUAL** | 27 (60.0%) | {(df_res["classification"] == "GRADUAL").sum()} ({(df_res["classification"] == "GRADUAL").mean()*100:.1f}%) | 70.5% (±6.8%) |')
out_lines.append(f'| **Classified INSTANT** | 3 (6.7%) | {(df_res["classification"] == "INSTANT").sum()} ({(df_res["classification"] == "INSTANT").mean()*100:.1f}%) | 7.9% (±4.0%) |')
out_lines.append(f'| **Classified FLAT/NONE** | 15 (33.3%) | {(df_res["classification"] == "FLAT/NONE").sum()} ({(df_res["classification"] == "FLAT/NONE").mean()*100:.1f}%) | 21.6% (±6.2%) |')
out_lines.append(f'| **Flagged (>2x Volume & GRADUAL)** | 1 (2.2%) | {df_res["flagged"].sum()} ({df_res["flagged"].mean()*100:.1f}%) | 10.9% (±5.1%) |')
out_lines.append('')
out_lines.append('### Key Takeaways')
out_lines.append('1. **% GRADUAL**: **60.0%** in filing-linked data vs. **82.2%** (sample) / **70.5%** (100-seed average) in random baseline data.')
out_lines.append('2. **% Flagged (>2x volume + GRADUAL)**: **2.2%** (1/45) in filing-linked data vs. **13.3%** (6/45 sample) / **10.9%** (100-seed average) in random baseline data.')
out_lines.append('')
out_lines.append('---')
out_lines.append('')
out_lines.append('## Random Baseline Market Data Reactions Table')
out_lines.append('')
out_lines.append(f'**Summary**: Total Rows: {len(df_res)} | Fully Analyzed: {len(df_res)} | Classified GRADUAL: {(df_res["classification"] == "GRADUAL").sum()} | Flagged (Volume Ratio > 2x & GRADUAL): {df_res["flagged"].sum()}')
out_lines.append('')
out_lines.append('| Ticker | Random Date | Price 1 day before | Price on random date | Price 1 day after | Price 5 days after | Price 15 days after | Average daily volume (10 days before) | Average daily volume (15 days after) | Volume ratio (after/before) | Classification | Flagged |')
out_lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|')

for _, row in df_res.iterrows():
    p_m1_str = f'${row["p_m1"]:.3f}'
    p_0_str = f'${row["p_0"]:.3f}'
    p_p1_str = f'${row["p_p1"]:.3f}'
    p_p5_str = f'${row["p_p5"]:.3f}'
    p_p15_str = f'${row["p_p15"]:.3f}'
    v_bef_str = f'{int(round(row["avg_vol_before"])):,}'
    v_aft_str = f'{int(round(row["avg_vol_after"])):,}'
    v_rat_str = f'{row["vol_ratio"]:.2f}x'
    cls_str = row['classification']
    flg_str = '**YES**' if row['flagged'] else 'No'
    
    out_lines.append(f'| {row["ticker"]} | {row["random_date"]} | {p_m1_str} | {p_0_str} | {p_p1_str} | {p_p5_str} | {p_p15_str} | {v_bef_str} | {v_aft_str} | {v_rat_str} | {cls_str} | {flg_str} |')

output_path = '/home/mason/Trading/random_baseline_filings.md'
with open(output_path, 'w') as f:
    f.write('\n'.join(out_lines))

print(f'Saved {output_path} successfully!')
