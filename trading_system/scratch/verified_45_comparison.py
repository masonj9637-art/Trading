"""
Verified 45-Ticker Comparison: YES vs NO
Same methodology as the original: 1000-seed Monte Carlo, Mann-Whitney U,
permutation p-values, Cohen's d, per-industry breakdown.

Adapts to the reality that Mining has 0 valid YES filings.
"""

import random
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('/home/mason/Trading/scratch/verified_45_results.csv')

yes_df = df[df['plausible'] == 'Yes'].reset_index(drop=True)
no_df  = df[df['plausible'] == 'No'].reset_index(drop=True)

print(f"VERIFIED 45-TICKER DATASET")
print(f"Total valid filings: {len(df)}")
print(f"YES: {len(yes_df)}  (Bio: {sum(yes_df['industry']=='Biotech')}, Min: {sum(yes_df['industry']=='Mining')}, Fin: {sum(yes_df['industry']=='Fintech')})")
print(f"NO:  {len(no_df)}  (Bio: {sum(no_df['industry']=='Biotech')}, Min: {sum(no_df['industry']=='Mining')}, Fin: {sum(no_df['industry']=='Fintech')})")

# ---- Helper ----
def group_stats(df_in):
    n = len(df_in)
    if n == 0:
        return {k: np.nan for k in ['n','pct_non_flat','pct_gradual','pct_instant','pct_flat',
                'pct_flagged','pct_vol2x','vol_ratio_mean','vol_ratio_med',
                'abs_15d_mean','abs_15d_med','abs_5d_mean','abs_5d_med',
                'abs_1d_mean','abs_1d_med','dir_15d_mean','dir_5d_mean','dir_1d_mean']}
    non_flat = (df_in['classification'] != 'FLAT/NONE').sum()
    return {
        'n': n,
        'pct_non_flat':  non_flat / n * 100,
        'pct_gradual':   (df_in['classification'] == 'GRADUAL').mean() * 100,
        'pct_instant':   (df_in['classification'] == 'INSTANT').mean() * 100,
        'pct_flat':      (df_in['classification'] == 'FLAT/NONE').mean() * 100,
        'pct_flagged':   df_in['flagged'].mean() * 100,
        'pct_vol2x':     df_in['vol_spike_2x'].mean() * 100,
        'vol_ratio_mean': df_in['vol_ratio'].mean(),
        'vol_ratio_med':  df_in['vol_ratio'].median(),
        'abs_15d_mean':  df_in['abs_15d'].mean(),
        'abs_15d_med':   df_in['abs_15d'].median(),
        'abs_5d_mean':   df_in['abs_5d'].mean(),
        'abs_5d_med':    df_in['abs_5d'].median(),
        'abs_1d_mean':   df_in['abs_1d'].mean(),
        'abs_1d_med':    df_in['abs_1d'].median(),
        'dir_15d_mean':  df_in['pct_15d'].mean(),
        'dir_5d_mean':   df_in['pct_5d'].mean(),
        'dir_1d_mean':   df_in['pct_1d'].mean(),
    }

yes_stats = group_stats(yes_df)

# ---- Monte Carlo: industry-matched random draw from NO pool ----
# Mining YES = 0, so we match industry proportions: Bio=8, Fin=8, Min=0
bio_yes_n = sum(yes_df['industry'] == 'Biotech')
fin_yes_n = sum(yes_df['industry'] == 'Fintech')
min_yes_n = sum(yes_df['industry'] == 'Mining')

bio_no = no_df[no_df['industry'] == 'Biotech']
fin_no = no_df[no_df['industry'] == 'Fintech']
min_no = no_df[no_df['industry'] == 'Mining']

print(f"\nMonte Carlo matching: draw {bio_yes_n} Bio + {fin_yes_n} Fin + {min_yes_n} Min = {bio_yes_n+fin_yes_n+min_yes_n} from NO pool")
print(f"NO pool available: Bio={len(bio_no)}, Fin={len(fin_no)}, Min={len(min_no)}")

N_SEEDS = 1000
mc_records = []

for seed in range(N_SEEDS):
    rng = np.random.RandomState(seed)
    parts = []
    if bio_yes_n > 0 and len(bio_no) >= bio_yes_n:
        parts.append(bio_no.sample(n=bio_yes_n, random_state=rng))
    if fin_yes_n > 0 and len(fin_no) >= fin_yes_n:
        parts.append(fin_no.sample(n=fin_yes_n, random_state=rng))
    if min_yes_n > 0 and len(min_no) >= min_yes_n:
        parts.append(min_no.sample(n=min_yes_n, random_state=rng))
    
    if parts:
        sample = pd.concat(parts)
        mc_records.append(group_stats(sample))

mc_df = pd.DataFrame(mc_records)

# ---- Full NO pool stats ----
no_full_stats = group_stats(no_df)

# ---- Print comparison ----
print("\n" + "="*115)
print("       VERIFIED 45-TICKER COMPARISON: YES (PREDICTED MOVERS) vs NO (RANDOM CONTROL)")
print("="*115)
print(f"  YES group N = {len(yes_df)}    |    NO MC matched N = {len(yes_df)} ({N_SEEDS} seeds)    |    NO Full Universe N = {len(no_df)}")
print(f"  NOTE: Mining has 0 valid YES filings — MC draws only from Biotech + Fintech NO pools")
print("-"*115)

fmt_lines = [
    ("% Non-Flat (moved ≥4%)",     'pct_non_flat', '.1f'),
    ("% GRADUAL",                   'pct_gradual',  '.1f'),
    ("% INSTANT",                   'pct_instant',  '.1f'),
    ("% FLAT/NONE",                 'pct_flat',     '.1f'),
    ("% Flagged (>2x Vol+GRADUAL)", 'pct_flagged',  '.1f'),
    ("% Volume Spike (>2x)",        'pct_vol2x',    '.1f'),
    ("Avg Volume Ratio",            'vol_ratio_mean','.2f'),
    ("Median Volume Ratio",         'vol_ratio_med', '.2f'),
    ("Avg Abs 15-day Move %",       'abs_15d_mean', '.2f'),
    ("Median Abs 15-day Move %",    'abs_15d_med',  '.2f'),
    ("Avg Abs 5-day Move %",        'abs_5d_mean',  '.2f'),
    ("Median Abs 5-day Move %",     'abs_5d_med',   '.2f'),
    ("Avg Abs 1-day Move %",        'abs_1d_mean',  '.2f'),
    ("Median Abs 1-day Move %",     'abs_1d_med',   '.2f'),
    ("Avg Dir 15-day Return %",     'dir_15d_mean', '.2f'),
    ("Avg Dir 5-day Return %",      'dir_5d_mean',  '.2f'),
    ("Avg Dir 1-day Return %",      'dir_1d_mean',  '.2f'),
]

print(f"  {'Metric':<40s}  {'YES':>10s}   {'NO (MC avg ± σ)':>22s}   {'NO (full)':>10s}")
print("-"*115)

for label, key, fmt in fmt_lines:
    y_val = f'{yes_stats[key]:{fmt}}'
    mc_mean = mc_df[key].mean()
    mc_std = mc_df[key].std()
    mc_str = f'{mc_mean:{fmt}} (±{mc_std:{fmt}})'
    nf_val = f'{no_full_stats[key]:{fmt}}'
    print(f"  {label:<40s}  {y_val:>10s}   {mc_str:>22s}   {nf_val:>10s}")

# ---- Statistical tests ----
print("\n" + "="*115)
print("       STATISTICAL SIGNIFICANCE TESTS")
print("="*115)

if len(yes_df) >= 3 and len(no_df) >= 3:
    u15, p15 = stats.mannwhitneyu(yes_df['abs_15d'], no_df['abs_15d'], alternative='greater')
    u5, p5   = stats.mannwhitneyu(yes_df['abs_5d'],  no_df['abs_5d'],  alternative='greater')
    u1, p1   = stats.mannwhitneyu(yes_df['abs_1d'],  no_df['abs_1d'],  alternative='greater')
    uv, pv   = stats.mannwhitneyu(yes_df['vol_ratio'],no_df['vol_ratio'],alternative='greater')
    
    print(f"\n  Mann-Whitney U (one-sided, YES > NO):")
    print(f"    abs_15d:   U={u15:.0f}, p={p15:.4f}  {'*' if p15<0.05 else ''}")
    print(f"    abs_5d:    U={u5:.0f},  p={p5:.4f}  {'*' if p5<0.05 else ''}")
    print(f"    abs_1d:    U={u1:.0f},  p={p1:.4f}  {'*' if p1<0.05 else ''}")
    print(f"    vol_ratio: U={uv:.0f},  p={pv:.4f}  {'*' if pv<0.05 else ''}")

    # Permutation tests
    yes_15d_mean = yes_df['abs_15d'].mean()
    mc_exceeds_15 = sum(1 for v in mc_df['abs_15d_mean'] if v >= yes_15d_mean)
    print(f"\n  Permutation ({N_SEEDS} seeds):")
    print(f"    YES abs_15d mean = {yes_15d_mean:.2f}%")
    print(f"    NO matched ≥ YES: {mc_exceeds_15}/{N_SEEDS} = {mc_exceeds_15/N_SEEDS*100:.1f}% (empirical p)")
    
    yes_5d_mean = yes_df['abs_5d'].mean()
    mc_exceeds_5 = sum(1 for v in mc_df['abs_5d_mean'] if v >= yes_5d_mean)
    print(f"    YES abs_5d mean  = {yes_5d_mean:.2f}%")
    print(f"    NO matched ≥ YES: {mc_exceeds_5}/{N_SEEDS} = {mc_exceeds_5/N_SEEDS*100:.1f}%")

    yes_1d_mean = yes_df['abs_1d'].mean()
    mc_exceeds_1 = sum(1 for v in mc_df['abs_1d_mean'] if v >= yes_1d_mean)
    print(f"    YES abs_1d mean  = {yes_1d_mean:.2f}%")
    print(f"    NO matched ≥ YES: {mc_exceeds_1}/{N_SEEDS} = {mc_exceeds_1/N_SEEDS*100:.1f}%")
    
    yes_nf = yes_stats['pct_non_flat']
    mc_nf_exceeds = sum(1 for v in mc_df['pct_non_flat'] if v >= yes_nf)
    print(f"    YES % non-flat   = {yes_nf:.1f}%")
    print(f"    NO matched ≥ YES: {mc_nf_exceeds}/{N_SEEDS} = {mc_nf_exceeds/N_SEEDS*100:.1f}%")
else:
    print("  INSUFFICIENT SAMPLE SIZE for Mann-Whitney U tests")

# ---- Effect sizes ----
def cohens_d(x, y):
    nx, ny = len(x), len(y)
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    pooled_std = np.sqrt(((nx-1)*vx + (ny-1)*vy) / (nx+ny-2))
    return (x.mean() - y.mean()) / pooled_std if pooled_std > 0 else 0

d15 = cohens_d(yes_df['abs_15d'], no_df['abs_15d'])
d5  = cohens_d(yes_df['abs_5d'],  no_df['abs_5d'])
d1  = cohens_d(yes_df['abs_1d'],  no_df['abs_1d'])
dv  = cohens_d(yes_df['vol_ratio'],no_df['vol_ratio'])

def d_label(d):
    if abs(d) >= 0.8: return 'large'
    if abs(d) >= 0.5: return 'medium'
    if abs(d) >= 0.2: return 'small'
    return 'negligible'

print(f"\n  Effect Sizes (Cohen's d, YES vs NO full):")
print(f"    abs_15d:   d = {d15:+.3f}  ({d_label(d15)})")
print(f"    abs_5d:    d = {d5:+.3f}  ({d_label(d5)})")
print(f"    abs_1d:    d = {d1:+.3f}  ({d_label(d1)})")
print(f"    vol_ratio: d = {dv:+.3f}  ({d_label(dv)})")

# ---- Power analysis note ----
print(f"\n  POWER NOTE: With YES N={len(yes_df)} and NO N={len(no_df)}, detecting a")
print(f"  medium effect (d=0.5) at α=0.05 requires ~64 per group (80% power).")
print(f"  This study is underpowered for medium effects and cannot detect small effects.")

# ---- By-Industry ----
print("\n" + "="*115)
print("       BY-INDUSTRY BREAKDOWN")
print("="*115)

for ind in ['Biotech', 'Mining', 'Fintech']:
    y_ind = yes_df[yes_df['industry'] == ind]
    n_ind = no_df[no_df['industry'] == ind]
    
    print(f"\n  {ind.upper()} (YES N={len(y_ind)}, NO N={len(n_ind)}):")
    
    if len(y_ind) == 0:
        print(f"    YES: No valid filings — comparison not possible")
        print(f"    NO:  Non-Flat={((n_ind['classification']!='FLAT/NONE').mean()*100):.0f}%  "
              f"AvgAbs15d={n_ind['abs_15d'].mean():.1f}%  AvgAbs5d={n_ind['abs_5d'].mean():.1f}%  "
              f"AvgAbs1d={n_ind['abs_1d'].mean():.1f}%  VolRatio={n_ind['vol_ratio'].mean():.2f}x  "
              f"Flagged={n_ind['flagged'].sum()}/{len(n_ind)}")
        continue
    
    print(f"    YES: Non-Flat={((y_ind['classification']!='FLAT/NONE').mean()*100):.0f}%  "
          f"AvgAbs15d={y_ind['abs_15d'].mean():.1f}%  AvgAbs5d={y_ind['abs_5d'].mean():.1f}%  "
          f"AvgAbs1d={y_ind['abs_1d'].mean():.1f}%  VolRatio={y_ind['vol_ratio'].mean():.2f}x  "
          f"Flagged={y_ind['flagged'].sum()}/{len(y_ind)}")
    print(f"    NO:  Non-Flat={((n_ind['classification']!='FLAT/NONE').mean()*100):.0f}%  "
          f"AvgAbs15d={n_ind['abs_15d'].mean():.1f}%  AvgAbs5d={n_ind['abs_5d'].mean():.1f}%  "
          f"AvgAbs1d={n_ind['abs_1d'].mean():.1f}%  VolRatio={n_ind['vol_ratio'].mean():.2f}x  "
          f"Flagged={n_ind['flagged'].sum()}/{len(n_ind)}")
    
    if len(y_ind) >= 3 and len(n_ind) >= 3:
        u_ind, p_ind = stats.mannwhitneyu(y_ind['abs_15d'], n_ind['abs_15d'], alternative='greater')
        d_ind = cohens_d(y_ind['abs_15d'], n_ind['abs_15d'])
        print(f"    Mann-Whitney U (abs_15d): U={u_ind:.0f}, p={p_ind:.4f}, d={d_ind:+.3f} ({d_label(d_ind)})")

# ---- Individual YES filings ----
print("\n" + "="*115)
print("       INDIVIDUAL YES FILINGS DETAIL")
print("="*115)
cols = ['ticker','industry','filing_date','items','classification','vol_ratio',
        'abs_1d','abs_5d','abs_15d','pct_15d','flagged','vol_spike_2x']
print(yes_df[cols].to_string(index=False))

# ---- Classification distribution ----
print("\n" + "="*115)
print("       CLASSIFICATION DISTRIBUTION")
print("="*115)
for label, sub in [('YES', yes_df), ('NO', no_df)]:
    total = len(sub)
    print(f"  {label} (N={total}):")
    for cls in ['INSTANT', 'GRADUAL', 'FLAT/NONE']:
        cnt = sum(sub['classification'] == cls)
        print(f"    {cls}: {cnt} ({cnt/total*100:.1f}%)")

print("\n" + "="*115)
print("DONE")
