"""
Yes vs No Filing Comparison — Content-Based Judgment Validation

Uses cached Alpaca price/volume reaction data from the three industry reports
(Biotech, Mining, Fintech).  Compares the 30 "Yes" (agent-predicted price mover)
filings against matched-count random draws from the "No" pool using 1000-seed
Monte Carlo, plus the full "No" universe for reference.

Classification logic (same as prior work):
  INSTANT: >=60% of total move in day-1, drift small relative to spike
  GRADUAL: Total move >= 4%, not instant
  FLAT/NONE: Total absolute 15-day move < 4%
  
  Flagged = GRADUAL + volume ratio >2x
"""

import random
import numpy as np
import pandas as pd
from scipy import stats

yes_df = pd.read_csv('/home/mason/Trading/scratch/yes_group_all_valid.csv')
no_df  = pd.read_csv('/home/mason/Trading/scratch/no_group_all_valid.csv')

print(f"YES group: {len(yes_df)} filings  ({yes_df.industry.value_counts().to_dict()})")
print(f"NO  group: {len(no_df)} filings  ({no_df.industry.value_counts().to_dict()})")

# ---- Helper ----
def group_stats(df, label):
    n = len(df)
    non_flat = (df['classification'] != 'FLAT/NONE').sum()
    return {
        'label': label,
        'n': n,
        'pct_gradual':   (df['classification'] == 'GRADUAL').mean() * 100,
        'pct_instant':   (df['classification'] == 'INSTANT').mean() * 100,
        'pct_flat':      (df['classification'] == 'FLAT/NONE').mean() * 100,
        'pct_non_flat':  non_flat / n * 100,
        'pct_flagged':   df['flagged'].mean() * 100,
        'pct_vol2x':     df['vol_spike_2x'].mean() * 100,
        'vol_ratio_mean': df['vol_ratio'].mean(),
        'vol_ratio_med':  df['vol_ratio'].median(),
        'abs_15d_mean':  df['abs_15d'].mean(),
        'abs_15d_med':   df['abs_15d'].median(),
        'abs_5d_mean':   df['abs_5d'].mean(),
        'abs_5d_med':    df['abs_5d'].median(),
        'abs_1d_mean':   df['abs_1d'].mean(),
        'abs_1d_med':    df['abs_1d'].median(),
        'dir_15d_mean':  df['pct_15d'].mean(),
        'dir_5d_mean':   df['pct_5d'].mean(),
        'dir_1d_mean':   df['pct_1d'].mean(),
    }

# ---- YES group stats ----
yes_stats = group_stats(yes_df, 'YES')

# ---- Monte Carlo matched sampling from NO pool ----
mining_yes_n  = (yes_df['industry'] == 'Mining').sum()
fintech_yes_n = (yes_df['industry'] == 'Fintech').sum()
biotech_yes_n = (yes_df['industry'] == 'Biotech').sum()

mining_no  = no_df[no_df['industry'] == 'Mining']
fintech_no = no_df[no_df['industry'] == 'Fintech']
biotech_no = no_df[no_df['industry'] == 'Biotech']

N_SEEDS = 1000
mc_records = []
mc_abs15_lists = []

for seed in range(N_SEEDS):
    rng = np.random.RandomState(seed)
    sample = pd.concat([
        mining_no.sample(n=mining_yes_n, random_state=rng),
        fintech_no.sample(n=fintech_yes_n, random_state=rng),
        biotech_no.sample(n=biotech_yes_n, random_state=rng),
    ])
    mc_records.append(group_stats(sample, f'NO_seed{seed}'))
    mc_abs15_lists.append(sample['abs_15d'].values)

mc_df = pd.DataFrame(mc_records)

# ---- Full NO pool stats ----
no_full_stats = group_stats(no_df, 'NO_FULL')

# ---- Print comparison ----
def pline(metric, yes_val, mc_mean, mc_std, no_full_val, fmt='.1f'):
    fmts = f'{{:{fmt}}}'
    y = fmts.format(yes_val)
    m = f'{fmts.format(mc_mean)} (±{fmts.format(mc_std)})'
    n = fmts.format(no_full_val)
    print(f"  {metric:<40s}  {y:>10s}   {m:>20s}   {n:>10s}")

print("\n" + "="*110)
print("                        DIRECT COMPARISON: YES (PREDICTED MOVERS) vs NO (RANDOM CONTROL)")
print("="*110)
print(f"  YES group N = {len(yes_df)}    |    NO Monte Carlo matched N = {len(yes_df)} (1000 seeds)    |    NO Full Universe N = {len(no_df)}")
print("-"*110)
print(f"  {'Metric':<40s}  {'YES':>10s}   {'NO (MC avg ± σ)':>20s}   {'NO (full)':>10s}")
print("-"*110)

metrics = [
    ('% Non-Flat (moved ≥4%)',    'pct_non_flat', '.1f'),
    ('% GRADUAL',                 'pct_gradual',  '.1f'),
    ('% INSTANT',                 'pct_instant',  '.1f'),
    ('% FLAT/NONE',               'pct_flat',     '.1f'),
    ('% Flagged (>2x Vol+GRADUAL)','pct_flagged', '.1f'),
    ('% Volume Spike (>2x)',      'pct_vol2x',    '.1f'),
    ('Avg Volume Ratio',          'vol_ratio_mean','.2f'),
    ('Median Volume Ratio',       'vol_ratio_med', '.2f'),
    ('Avg Abs 15-day Move %',     'abs_15d_mean', '.2f'),
    ('Median Abs 15-day Move %',  'abs_15d_med',  '.2f'),
    ('Avg Abs 5-day Move %',      'abs_5d_mean',  '.2f'),
    ('Median Abs 5-day Move %',   'abs_5d_med',   '.2f'),
    ('Avg Abs 1-day Move %',      'abs_1d_mean',  '.2f'),
    ('Median Abs 1-day Move %',   'abs_1d_med',   '.2f'),
    ('Avg Directional 15-day %',  'dir_15d_mean', '.2f'),
    ('Avg Directional 5-day %',   'dir_5d_mean',  '.2f'),
    ('Avg Directional 1-day %',   'dir_1d_mean',  '.2f'),
]

for label, key, fmt in metrics:
    pline(label, yes_stats[key], mc_df[key].mean(), mc_df[key].std(), no_full_stats[key], fmt)

# ---- Statistical tests ----
print("\n" + "="*110)
print("                        STATISTICAL SIGNIFICANCE TESTS")
print("="*110)

# 1. Mann-Whitney U on abs_15d: YES vs full NO pool
u_stat, u_p = stats.mannwhitneyu(yes_df['abs_15d'], no_df['abs_15d'], alternative='greater')
print(f"\n  Mann-Whitney U (YES abs_15d > NO abs_15d): U={u_stat:.0f}, p={u_p:.4f}")

u_stat5, u_p5 = stats.mannwhitneyu(yes_df['abs_5d'], no_df['abs_5d'], alternative='greater')
print(f"  Mann-Whitney U (YES abs_5d  > NO abs_5d):  U={u_stat5:.0f}, p={u_p5:.4f}")

u_stat1, u_p1 = stats.mannwhitneyu(yes_df['abs_1d'], no_df['abs_1d'], alternative='greater')
print(f"  Mann-Whitney U (YES abs_1d  > NO abs_1d):  U={u_stat1:.0f}, p={u_p1:.4f}")

u_vol, u_volp = stats.mannwhitneyu(yes_df['vol_ratio'], no_df['vol_ratio'], alternative='greater')
print(f"  Mann-Whitney U (YES vol_ratio > NO vol_ratio): U={u_vol:.0f}, p={u_volp:.4f}")

# 2. Permutation test: fraction of MC seeds where NO matched-sample abs_15d_mean >= YES abs_15d_mean
yes_abs15_mean = yes_df['abs_15d'].mean()
mc_exceeds = sum(1 for v in mc_df['abs_15d_mean'] if v >= yes_abs15_mean)
print(f"\n  Permutation (1000 seeds): YES abs_15d mean = {yes_abs15_mean:.2f}%")
print(f"    NO matched samples with mean >= YES mean: {mc_exceeds}/{N_SEEDS} = {mc_exceeds/N_SEEDS*100:.1f}% (empirical p-value)")

yes_abs5_mean = yes_df['abs_5d'].mean()
mc_exceeds5 = sum(1 for v in mc_df['abs_5d_mean'] if v >= yes_abs5_mean)
print(f"  Permutation (1000 seeds): YES abs_5d mean = {yes_abs5_mean:.2f}%")
print(f"    NO matched samples with mean >= YES mean: {mc_exceeds5}/{N_SEEDS} = {mc_exceeds5/N_SEEDS*100:.1f}%")

# 3. % non-flat comparison
yes_nf = yes_stats['pct_non_flat']
mc_nf_exceeds = sum(1 for v in mc_df['pct_non_flat'] if v >= yes_nf)
print(f"\n  Permutation: YES % non-flat = {yes_nf:.1f}%")
print(f"    NO matched samples with % non-flat >= YES: {mc_nf_exceeds}/{N_SEEDS} = {mc_nf_exceeds/N_SEEDS*100:.1f}%")

# ---- By-industry breakdown ----
print("\n" + "="*110)
print("                        BY-INDUSTRY BREAKDOWN")
print("="*110)

for ind in ['Mining', 'Fintech', 'Biotech']:
    y_ind = yes_df[yes_df['industry'] == ind]
    n_ind = no_df[no_df['industry'] == ind]
    if len(y_ind) == 0:
        continue
    print(f"\n  {ind.upper()} (YES N={len(y_ind)}, NO N={len(n_ind)}):")
    print(f"    YES: Non-Flat={((y_ind['classification']!='FLAT/NONE').mean()*100):.0f}%  "
          f"AvgAbs15d={y_ind['abs_15d'].mean():.1f}%  AvgAbs5d={y_ind['abs_5d'].mean():.1f}%  "
          f"AvgAbs1d={y_ind['abs_1d'].mean():.1f}%  VolRatio={y_ind['vol_ratio'].mean():.2f}x  "
          f"Flagged={y_ind['flagged'].sum()}/{len(y_ind)}")
    print(f"    NO:  Non-Flat={((n_ind['classification']!='FLAT/NONE').mean()*100):.0f}%  "
          f"AvgAbs15d={n_ind['abs_15d'].mean():.1f}%  AvgAbs5d={n_ind['abs_5d'].mean():.1f}%  "
          f"AvgAbs1d={n_ind['abs_1d'].mean():.1f}%  VolRatio={n_ind['vol_ratio'].mean():.2f}x  "
          f"Flagged={n_ind['flagged'].sum()}/{len(n_ind)}")

# ---- Individual YES filings detail ----
print("\n" + "="*110)
print("                        INDIVIDUAL YES FILINGS DETAIL")
print("="*110)
cols = ['ticker', 'industry', 'filing_date', 'classification', 'vol_ratio', 
        'abs_1d', 'abs_5d', 'abs_15d', 'pct_15d', 'flagged', 'vol_spike_2x']
print(yes_df[cols].to_string(index=False))

# ---- Effect Size (Cohen's d) ----
def cohens_d(x, y):
    nx, ny = len(x), len(y)
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    pooled_std = np.sqrt(((nx-1)*vx + (ny-1)*vy) / (nx+ny-2))
    return (x.mean() - y.mean()) / pooled_std if pooled_std > 0 else 0

d15 = cohens_d(yes_df['abs_15d'], no_df['abs_15d'])
d5  = cohens_d(yes_df['abs_5d'], no_df['abs_5d'])
d1  = cohens_d(yes_df['abs_1d'], no_df['abs_1d'])
dv  = cohens_d(yes_df['vol_ratio'], no_df['vol_ratio'])

print(f"\n  Effect Sizes (Cohen's d, YES vs NO full):")
print(f"    abs_15d:   d = {d15:.3f}  ({'large' if abs(d15)>=0.8 else 'medium' if abs(d15)>=0.5 else 'small'})")
print(f"    abs_5d:    d = {d5:.3f}  ({'large' if abs(d5)>=0.8 else 'medium' if abs(d5)>=0.5 else 'small'})")
print(f"    abs_1d:    d = {d1:.3f}  ({'large' if abs(d1)>=0.8 else 'medium' if abs(d1)>=0.5 else 'small'})")
print(f"    vol_ratio: d = {dv:.3f}  ({'large' if abs(dv)>=0.8 else 'medium' if abs(dv)>=0.5 else 'small'})")

print("\n" + "="*110)
print("DONE")
