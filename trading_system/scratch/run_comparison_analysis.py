import os
import random
import re
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

# Load credentials
load_dotenv('/home/mason/Trading/.env')
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
client = StockHistoricalDataClient(api_key, secret_key)

def parse_review_file(file_path, industry_name):
    with open(file_path, 'r') as f:
        content = f.read()
    
    filings = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith('|') and not 'Ticker' in line and not '|---|' in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 8:
                ticker = parts[0]
                company = parts[1]
                mcap = parts[2]
                f_date = parts[3]
                f_url = parts[4]
                item_types = parts[5]
                summary = parts[6]
                plausible = parts[7] # **Yes** or **No**
                
                is_yes = 'Yes' in plausible
                
                filings.append({
                    'ticker': ticker,
                    'company': company,
                    'mcap': mcap,
                    'filing_date': f_date,
                    'filing_url': f_url,
                    'item_types': item_types,
                    'summary': summary,
                    'plausible_mover': 'Yes' if is_yes else 'No',
                    'industry': industry_name
                })
    return filings

mining_filings = parse_review_file('/home/mason/Trading/scratch/mining_8k_review.md', 'Mining')
fintech_filings = parse_review_file('/home/mason/Trading/scratch/fintech_8k_review.md', 'Fintech')
biotech_filings = parse_review_file('/home/mason/Trading/scratch/biotech_8k_review.md', 'Biotech')

all_filings = mining_filings + fintech_filings + biotech_filings

print(f"Total Mining Filings: {len(mining_filings)} (Yes: {sum(1 for f in mining_filings if f['plausible_mover']=='Yes')}, No: {sum(1 for f in mining_filings if f['plausible_mover']=='No')})")
print(f"Total Fintech Filings: {len(fintech_filings)} (Yes: {sum(1 for f in fintech_filings if f['plausible_mover']=='Yes')}, No: {sum(1 for f in fintech_filings if f['plausible_mover']=='No')})")
print(f"Total Biotech Filings: {len(biotech_filings)} (Yes: {sum(1 for f in biotech_filings if f['plausible_mover']=='Yes')}, No: {sum(1 for f in biotech_filings if f['plausible_mover']=='No')})")

# Separate Yes and No per industry
yes_group = [f for f in all_filings if f['plausible_mover'] == 'Yes']

random.seed(42)
mining_no = [f for f in mining_filings if f['plausible_mover'] == 'No']
fintech_no = [f for f in fintech_filings if f['plausible_mover'] == 'No']
biotech_no = [f for f in biotech_filings if f['plausible_mover'] == 'No']

sampled_mining_no = random.sample(mining_no, sum(1 for f in mining_filings if f['plausible_mover']=='Yes'))
sampled_fintech_no = random.sample(fintech_no, sum(1 for f in fintech_filings if f['plausible_mover']=='Yes'))
sampled_biotech_no = random.sample(biotech_no, sum(1 for f in biotech_filings if f['plausible_mover']=='Yes'))

no_group = sampled_mining_no + sampled_fintech_no + sampled_biotech_no

print(f"\nYes Group Count: {len(yes_group)}")
print(f"No Group Count: {len(no_group)}")

# Get all unique tickers
all_tickers = sorted(list(set([f['ticker'] for f in yes_group + no_group])))

print(f"\nFetching Alpaca bars for {len(all_tickers)} unique tickers...")

req = StockBarsRequest(
    symbol_or_symbols=all_tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2025, 5, 1),
    end=datetime(2026, 7, 24),
    feed=DataFeed.IEX
)

bars_df = client.get_stock_bars(req).df.reset_index()
bars_df['date'] = pd.to_datetime(bars_df['timestamp']).dt.tz_localize(None).dt.normalize()

def analyze_group(group_filings, group_label):
    results = []
    insufficient = []
    
    for idx, f in enumerate(group_filings):
        ticker = f['ticker']
        f_date = pd.to_datetime(f['filing_date']).normalize()
        
        t_bars = bars_df[bars_df['symbol'] == ticker].sort_values('date').reset_index(drop=True)
        
        t0_matches = t_bars[t_bars['date'] == f_date]
        if t0_matches.empty:
            insufficient.append({
                'ticker': ticker,
                'filing_date': f['filing_date'],
                'reason': 'Filing date not in bar data'
            })
            continue
            
        t0_idx = t0_matches.index[0]
        
        if t0_idx < 10:
            insufficient.append({
                'ticker': ticker,
                'filing_date': f['filing_date'],
                'reason': f'Fewer than 10 pre-days (only {t0_idx})'
            })
            continue
            
        if t0_idx + 15 >= len(t_bars):
            avail_after = len(t_bars) - 1 - t0_idx
            insufficient.append({
                'ticker': ticker,
                'filing_date': f['filing_date'],
                'reason': f'Fewer than 15 post-days (only {avail_after})'
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
        pct_5d = (p_p5 - p_m1) / p_m1 * 100.0
        pct_day1 = (p_p1 - p_m1) / p_m1 * 100.0
        pct_drift = (p_p15 - p_p1) / p_m1 * 100.0
        
        abs_tot = abs(pct_total)
        abs_5d = abs(pct_5d)
        abs_d1 = abs(pct_day1)
        frac_day1 = pct_day1 / pct_total if pct_total != 0 else 0
        
        if abs_tot < 4.0:
            classification = "FLAT/NONE"
        elif (frac_day1 >= 0.60 and abs(pct_drift) <= max(3.5, 0.4 * abs_d1)) or (abs_d1 >= 10.0 and frac_day1 >= 0.50 and abs(pct_drift) <= 0.5 * abs_d1):
            classification = "INSTANT"
        else:
            classification = "GRADUAL"
            
        flagged = (vol_ratio > 2.0) and (classification == "GRADUAL")
        vol_spike_2x = (vol_ratio > 2.0)
        
        results.append({
            'group': group_label,
            'ticker': ticker,
            'company': f['company'],
            'industry': f['industry'],
            'filing_date': f['filing_date'],
            'p_m1': p_m1,
            'p_0': p_0,
            'p_p1': p_p1,
            'p_p5': p_p5,
            'p_p15': p_p15,
            'avg_vol_before': avg_vol_before,
            'avg_vol_after': avg_vol_after,
            'vol_ratio': vol_ratio,
            'pct_1d': pct_day1,
            'pct_5d': pct_5d,
            'pct_15d': pct_total,
            'abs_1d': abs_d1,
            'abs_5d': abs_5d,
            'abs_15d': abs_tot,
            'classification': classification,
            'flagged': flagged,
            'vol_spike_2x': vol_spike_2x
        })
    return pd.DataFrame(results), insufficient

df_yes, insuf_yes = analyze_group(yes_group, "Yes")
df_no, insuf_no = analyze_group(no_group, "No")

print("\n=== YES GROUP RESULTS ===")
print(f"Total Analyzed: {len(df_yes)}, Insufficient: {len(insuf_yes)}")
if len(insuf_yes) > 0:
    print("Insufficient:", insuf_yes)

print("\n=== NO GROUP RESULTS ===")
print(f"Total Analyzed: {len(df_no)}, Insufficient: {len(insuf_no)}")
if len(insuf_no) > 0:
    print("Insufficient:", insuf_no)

def print_metrics(df, label):
    print(f"\n--- Metrics Summary: {label} (N = {len(df)}) ---")
    print(f"Classified GRADUAL: {(df['classification']=='GRADUAL').sum()} ({(df['classification']=='GRADUAL').mean()*100:.1f}%)")
    print(f"Classified INSTANT: {(df['classification']=='INSTANT').sum()} ({(df['classification']=='INSTANT').mean()*100:.1f}%)")
    print(f"Classified FLAT/NONE: {(df['classification']=='FLAT/NONE').sum()} ({(df['classification']=='FLAT/NONE').mean()*100:.1f}%)")
    print(f"Flagged (>2x Volume & GRADUAL): {df['flagged'].sum()} ({df['flagged'].mean()*100:.1f}%)")
    print(f"Volume Ratio > 2x: {df['vol_spike_2x'].sum()} ({df['vol_spike_2x'].mean()*100:.1f}%)")
    print(f"Mean Volume Ratio: {df['vol_ratio'].mean():.2f}x (Median: {df['vol_ratio'].median():.2f}x)")
    print(f"Mean Abs 15-day Price Move: {df['abs_15d'].mean():.2f}% (Median: {df['abs_15d'].median():.2f}%)")
    print(f"Mean Abs 5-day Price Move: {df['abs_5d'].mean():.2f}% (Median: {df['abs_5d'].median():.2f}%)")
    print(f"Mean Abs 1-day Price Move: {df['abs_1d'].mean():.2f}% (Median: {df['abs_1d'].median():.2f}%)")
    print(f"Mean Directional 15-day Return: {df['pct_15d'].mean():.2f}%")
    print(f"Mean Directional 5-day Return: {df['pct_5d'].mean():.2f}%")
    print(f"Mean Directional 1-day Return: {df['pct_1d'].mean():.2f}%")

print_metrics(df_yes, "YES Group")
print_metrics(df_no, "NO Group (Random Matched Sample)")

# Also save detailed results to CSV/JSON for inspection
df_yes.to_csv('/home/mason/Trading/scratch/yes_group_results.csv', index=False)
df_no.to_csv('/home/mason/Trading/scratch/no_group_results.csv', index=False)
