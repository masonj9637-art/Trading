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
                plausible = parts[7]
                
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
all_tickers = sorted(list(set([f['ticker'] for f in all_filings])))

print(f"Fetching bars for ALL {len(all_tickers)} tickers...")

req = StockBarsRequest(
    symbol_or_symbols=all_tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2025, 5, 1),
    end=datetime(2026, 7, 24),
    feed=DataFeed.IEX
)

bars_df = client.get_stock_bars(req).df.reset_index()
bars_df['date'] = pd.to_datetime(bars_df['timestamp']).dt.tz_localize(None).dt.normalize()

def process_filing_list(filing_list):
    results = []
    insufficient = []
    
    for idx, f in enumerate(filing_list):
        ticker = f['ticker']
        f_date = pd.to_datetime(f['filing_date']).normalize()
        
        t_bars = bars_df[bars_df['symbol'] == ticker].sort_values('date').reset_index(drop=True)
        
        t0_matches = t_bars[t_bars['date'] == f_date]
        if t0_matches.empty:
            insufficient.append({
                'ticker': ticker,
                'filing_date': f['filing_date'],
                'industry': f['industry'],
                'plausible': f['plausible_mover'],
                'reason': 'Filing date not in bar data'
            })
            continue
            
        t0_idx = t0_matches.index[0]
        
        if t0_idx < 10:
            insufficient.append({
                'ticker': ticker,
                'filing_date': f['filing_date'],
                'industry': f['industry'],
                'plausible': f['plausible_mover'],
                'reason': f'Fewer than 10 pre-days ({t0_idx})'
            })
            continue
            
        if t0_idx + 15 >= len(t_bars):
            avail_after = len(t_bars) - 1 - t0_idx
            insufficient.append({
                'ticker': ticker,
                'filing_date': f['filing_date'],
                'industry': f['industry'],
                'plausible': f['plausible_mover'],
                'reason': f'Fewer than 15 post-days ({avail_after})'
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
            'ticker': ticker,
            'company': f['company'],
            'industry': f['industry'],
            'filing_date': f['filing_date'],
            'plausible': f['plausible_mover'],
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
    return pd.DataFrame(results), pd.DataFrame(insufficient)

df_all_res, df_all_insuf = process_filing_list(all_filings)

df_yes_all = df_all_res[df_all_res['plausible'] == 'Yes'].reset_index(drop=True)
df_no_all = df_all_res[df_all_res['plausible'] == 'No'].reset_index(drop=True)

print(f"\n--- TOTAL VALID DATA COVERAGE ---")
print(f"Total 'Yes' Filings Evaluated: {sum(1 for f in all_filings if f['plausible_mover']=='Yes')} -> Valid Bar Windows: {len(df_yes_all)} (Mining: {sum(df_yes_all['industry']=='Mining')}, Fintech: {sum(df_yes_all['industry']=='Fintech')}, Biotech: {sum(df_yes_all['industry']=='Biotech')})")
print(f"Total 'No' Filings Evaluated: {sum(1 for f in all_filings if f['plausible_mover']=='No')} -> Valid Bar Windows: {len(df_no_all)} (Mining: {sum(df_no_all['industry']=='Mining')}, Fintech: {sum(df_no_all['industry']=='Fintech')}, Biotech: {sum(df_no_all['industry']=='Biotech')})")

# 100-Seed Monte Carlo Matched Random Sampling for 'No' Group
# Matching target count per industry equal to valid 'Yes' filings per industry:
mining_yes_cnt = sum(df_yes_all['industry'] == 'Mining')
fintech_yes_cnt = sum(df_yes_all['industry'] == 'Fintech')
biotech_yes_cnt = sum(df_yes_all['industry'] == 'Biotech')

mining_no_valid = df_no_all[df_no_all['industry'] == 'Mining']
fintech_no_valid = df_no_all[df_no_all['industry'] == 'Fintech']
biotech_no_valid = df_no_all[df_no_all['industry'] == 'Biotech']

seed_stats = []
for seed in range(100):
    random.seed(seed)
    s_m = mining_no_valid.sample(n=mining_yes_cnt, random_state=seed)
    s_f = fintech_no_valid.sample(n=fintech_yes_cnt, random_state=seed)
    s_b = biotech_no_valid.sample(n=biotech_yes_cnt, random_state=seed)
    sample_df = pd.concat([s_m, s_f, s_b])
    
    seed_stats.append({
        'gradual_pct': (sample_df['classification'] == 'GRADUAL').mean() * 100,
        'instant_pct': (sample_df['classification'] == 'INSTANT').mean() * 100,
        'flat_pct': (sample_df['classification'] == 'FLAT/NONE').mean() * 100,
        'flagged_pct': sample_df['flagged'].mean() * 100,
        'vol_spike_2x_pct': sample_df['vol_spike_2x'].mean() * 100,
        'vol_ratio_mean': sample_df['vol_ratio'].mean(),
        'abs_15d_mean': sample_df['abs_15d'].mean(),
        'abs_5d_mean': sample_df['abs_5d'].mean(),
        'abs_1d_mean': sample_df['abs_1d'].mean(),
        'pct_15d_mean': sample_df['pct_15d'].mean(),
        'pct_5d_mean': sample_df['pct_5d'].mean(),
        'pct_1d_mean': sample_df['pct_1d'].mean()
    })

df_mc = pd.DataFrame(seed_stats)

print("\n========================================================")
print("              DIRECT COMPARISON SUMMARY                 ")
print("========================================================")

print(f"\n1. YES GROUP (AGENT PREDICTED PRICE MOVERS, N={len(df_yes_all)})")
print(f"   - % Classified GRADUAL:               {(df_yes_all['classification']=='GRADUAL').mean()*100:.1f}% ({sum(df_yes_all['classification']=='GRADUAL')}/{len(df_yes_all)})")
print(f"   - % Classified INSTANT:               {(df_yes_all['classification']=='INSTANT').mean()*100:.1f}% ({sum(df_yes_all['classification']=='INSTANT')}/{len(df_yes_all)})")
print(f"   - % Classified FLAT/NONE:             {(df_yes_all['classification']=='FLAT/NONE').mean()*100:.1f}% ({sum(df_yes_all['classification']=='FLAT/NONE')}/{len(df_yes_all)})")
print(f"   - % FLAGGED (>2x Vol & GRADUAL):       {df_yes_all['flagged'].mean()*100:.1f}% ({df_yes_all['flagged'].sum()}/{len(df_yes_all)})")
print(f"   - % Volume Spike (>2x Vol):           {df_yes_all['vol_spike_2x'].mean()*100:.1f}% ({df_yes_all['vol_spike_2x'].sum()}/{len(df_yes_all)})")
print(f"   - Avg Volume Ratio:                   {df_yes_all['vol_ratio'].mean():.2f}x (Median: {df_yes_all['vol_ratio'].median():.2f}x)")
print(f"   - Avg Abs 15-day Price Move Magnitude: {df_yes_all['abs_15d'].mean():.2f}% (Median: {df_yes_all['abs_15d'].median():.2f}%)")
print(f"   - Avg Abs 5-day Price Move Magnitude:  {df_yes_all['abs_5d'].mean():.2f}% (Median: {df_yes_all['abs_5d'].median():.2f}%)")
print(f"   - Avg Abs 1-day Price Move Magnitude:  {df_yes_all['abs_1d'].mean():.2f}% (Median: {df_yes_all['abs_1d'].median():.2f}%)")
print(f"   - Avg Directional 15-day Return:       {df_yes_all['pct_15d'].mean():.2f}%")
print(f"   - Avg Directional 5-day Return:        {df_yes_all['pct_5d'].mean():.2f}%")
print(f"   - Avg Directional 1-day Return:        {df_yes_all['pct_1d'].mean():.2f}%")

print(f"\n2. NO GROUP - 100-SEED MONTE CARLO MATCHED SAMPLE AVERAGE (N={len(df_yes_all)})")
print(f"   - % Classified GRADUAL:               {df_mc['gradual_pct'].mean():.1f}% (±{df_mc['gradual_pct'].std():.1f}%)")
print(f"   - % Classified INSTANT:               {df_mc['instant_pct'].mean():.1f}% (±{df_mc['instant_pct'].std():.1f}%)")
print(f"   - % Classified FLAT/NONE:             {df_mc['flat_pct'].mean():.1f}% (±{df_mc['flat_pct'].std():.1f}%)")
print(f"   - % FLAGGED (>2x Vol & GRADUAL):       {df_mc['flagged_pct'].mean():.1f}% (±{df_mc['flagged_pct'].std():.1f}%)")
print(f"   - % Volume Spike (>2x Vol):           {df_mc['vol_spike_2x_pct'].mean():.1f}% (±{df_mc['vol_spike_2x_pct'].std():.1f}%)")
print(f"   - Avg Volume Ratio:                   {df_mc['vol_ratio_mean'].mean():.2f}x")
print(f"   - Avg Abs 15-day Price Move Magnitude: {df_mc['abs_15d_mean'].mean():.2f}%")
print(f"   - Avg Abs 5-day Price Move Magnitude:  {df_mc['abs_5d_mean'].mean():.2f}%")
print(f"   - Avg Abs 1-day Price Move Magnitude:  {df_mc['abs_1d_mean'].mean():.2f}%")
print(f"   - Avg Directional 15-day Return:       {df_mc['pct_15d_mean'].mean():.2f}%")
print(f"   - Avg Directional 5-day Return:        {df_mc['pct_5d_mean'].mean():.2f}%")
print(f"   - Avg Directional 1-day Return:        {df_mc['pct_1d_mean'].mean():.2f}%")

print(f"\n3. NO GROUP - ALL VALID 'NO' FILINGS POOL (FULL UNIVERSE, N={len(df_no_all)})")
print(f"   - % Classified GRADUAL:               {(df_no_all['classification']=='GRADUAL').mean()*100:.1f}% ({sum(df_no_all['classification']=='GRADUAL')}/{len(df_no_all)})")
print(f"   - % Classified INSTANT:               {(df_no_all['classification']=='INSTANT').mean()*100:.1f}% ({sum(df_no_all['classification']=='INSTANT')}/{len(df_no_all)})")
print(f"   - % Classified FLAT/NONE:             {(df_no_all['classification']=='FLAT/NONE').mean()*100:.1f}% ({sum(df_no_all['classification']=='FLAT/NONE')}/{len(df_no_all)})")
print(f"   - % FLAGGED (>2x Vol & GRADUAL):       {df_no_all['flagged'].mean()*100:.1f}% ({df_no_all['flagged'].sum()}/{len(df_no_all)})")
print(f"   - % Volume Spike (>2x Vol):           {df_no_all['vol_spike_2x'].mean()*100:.1f}% ({df_no_all['vol_spike_2x'].sum()}/{len(df_no_all)})")
print(f"   - Avg Volume Ratio:                   {df_no_all['vol_ratio'].mean():.2f}x (Median: {df_no_all['vol_ratio'].median():.2f}x)")
print(f"   - Avg Abs 15-day Price Move Magnitude: {df_no_all['abs_15d'].mean():.2f}% (Median: {df_no_all['abs_15d'].median():.2f}%)")
print(f"   - Avg Abs 5-day Price Move Magnitude:  {df_no_all['abs_5d'].mean():.2f}% (Median: {df_no_all['abs_5d'].median():.2f}%)")
print(f"   - Avg Abs 1-day Price Move Magnitude:  {df_no_all['abs_1d'].mean():.2f}% (Median: {df_no_all['abs_1d'].median():.2f}%)")
print(f"   - Avg Directional 15-day Return:       {df_no_all['pct_15d'].mean():.2f}%")
print(f"   - Avg Directional 5-day Return:        {df_no_all['pct_5d'].mean():.2f}%")
print(f"   - Avg Directional 1-day Return:        {df_no_all['pct_1d'].mean():.2f}%")

print("\n--- BY INDUSTRY BREAKDOWN ---")
for ind in ['Mining', 'Fintech', 'Biotech']:
    y_ind = df_yes_all[df_yes_all['industry'] == ind]
    n_ind = df_no_all[df_no_all['industry'] == ind]
    print(f"\n{ind.upper()}:")
    print(f"  YES (N={len(y_ind)}): Flagged={y_ind['flagged'].mean()*100:.1f}%, Vol>2x={y_ind['vol_spike_2x'].mean()*100:.1f}%, Avg VolRatio={y_ind['vol_ratio'].mean():.2f}x, Avg Abs15d={y_ind['abs_15d'].mean():.2f}%, Avg Abs5d={y_ind['abs_5d'].mean():.2f}%, Avg Abs1d={y_ind['abs_1d'].mean():.2f}%")
    print(f"  NO  (N={len(n_ind)}): Flagged={n_ind['flagged'].mean()*100:.1f}%, Vol>2x={n_ind['vol_spike_2x'].mean()*100:.1f}%, Avg VolRatio={n_ind['vol_ratio'].mean():.2f}x, Avg Abs15d={n_ind['abs_15d'].mean():.2f}%, Avg Abs5d={n_ind['abs_5d'].mean():.2f}%, Avg Abs1d={n_ind['abs_1d'].mean():.2f}%")

# Save outputs
df_yes_all.to_csv('/home/mason/Trading/scratch/yes_group_all_valid.csv', index=False)
df_no_all.to_csv('/home/mason/Trading/scratch/no_group_all_valid.csv', index=False)
