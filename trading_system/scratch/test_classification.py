import pandas as pd
import numpy as np

from process_bars import results, insufficient_data

df = pd.DataFrame(results)

df['pct_total'] = (df['p_p15'] - df['p_m1']) / df['p_m1'] * 100.0
df['pct_day1'] = (df['p_p1'] - df['p_m1']) / df['p_m1'] * 100.0
df['pct_day5'] = (df['p_p5'] - df['p_m1']) / df['p_m1'] * 100.0
df['pct_drift'] = (df['p_p15'] - df['p_p1']) / df['p_m1'] * 100.0

def classify_row(row):
    pct_total = row['pct_total']
    pct_day1 = row['pct_day1']
    pct_drift = row['pct_drift']
    abs_tot = abs(pct_total)
    abs_d1 = abs(pct_day1)
    
    # 1. FLAT/NONE: Total move under 4% (no meaningful price change in either direction)
    if abs_tot < 4.0:
        return "FLAT/NONE"
    
    # 2. INSTANT: Most of total price change happened by day 1, with little further drift afterward
    # Condition: Day 1 move is in same direction as total move, accounts for >= 60% of total move,
    # AND subsequent drift is small (|drift| <= 3.5% or drift is <= 30% of day 1 move).
    frac_day1 = pct_day1 / pct_total if pct_total != 0 else 0
    if frac_day1 >= 0.60 and abs(pct_drift) <= max(3.5, 0.4 * abs_d1):
        return "INSTANT"
    
    # Also INSTANT if day 1 had a massive move (e.g. >= 10%) and total move is of similar magnitude, even if drift fluctuated back slightly
    if abs_d1 >= 10.0 and frac_day1 >= 0.50 and abs(pct_drift) <= 0.5 * abs_d1:
        return "INSTANT"

    # 3. GRADUAL: Otherwise, if total move >= 4% and it wasn't instant, price moved across the window
    return "GRADUAL"

df['classification'] = df.apply(classify_row, axis=1)
df['flagged'] = (df['vol_ratio'] > 2.0) & (df['classification'] == "GRADUAL")

print(f"Total processed rows: {len(df)}")
print(f"GRADUAL count: {(df['classification'] == 'GRADUAL').sum()}")
print(f"INSTANT count: {(df['classification'] == 'INSTANT').sum()}")
print(f"FLAT/NONE count: {(df['classification'] == 'FLAT/NONE').sum()}")
print(f"Flagged count (VolRatio > 2.0 AND GRADUAL): {df['flagged'].sum()}")

print("\n--- Detailed Summary Table ---")
for idx, r in df.iterrows():
    flag_str = " *** FLAGGED ***" if r['flagged'] else ""
    print(f"Row {r['row_id']:2d} | {r['ticker']:4s} | {r['filing_date']} | P-1:{r['p_m1']:6.3f} | P0:{r['p_0']:6.3f} | P+1:{r['p_p1']:6.3f} | P+5:{r['p_p5']:6.3f} | P+15:{r['p_p15']:6.3f} | V_bef:{r['avg_vol_before']:8.1f} | V_aft:{r['avg_vol_after']:8.1f} | VolRatio:{r['vol_ratio']:5.2f}x | Tot%:{r['pct_total']:+6.2f}% | D1%:{r['pct_day1']:+6.2f}% | Class: {r['classification']:9s}{flag_str}")
