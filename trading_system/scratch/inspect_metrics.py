import pandas as pd
import numpy as np

# Load processed bars from previous run
res_df = pd.read_csv('/tmp/processed_filings_bars.csv') if False else None

from process_bars import results, insufficient_data

df = pd.DataFrame(results)

df['pct_total'] = (df['p_p15'] - df['p_m1']) / df['p_m1'] * 100.0
df['pct_day1'] = (df['p_p1'] - df['p_m1']) / df['p_m1'] * 100.0
df['pct_day5'] = (df['p_p5'] - df['p_m1']) / df['p_m1'] * 100.0
df['pct_drift'] = (df['p_p15'] - df['p_p1']) / df['p_m1'] * 100.0

df['frac_day1'] = np.where(df['pct_total'] != 0, df['pct_day1'] / df['pct_total'], 0)

for idx, row in df.iterrows():
    print(f"Row {row['row_id']:2d} | {row['ticker']:4s} | {row['filing_date']} | P_-1:{row['p_m1']:6.3f} | P_0:{row['p_0']:6.3f} | P_+1:{row['p_p1']:6.3f} | P_+5:{row['p_p5']:6.3f} | P_+15:{row['p_p15']:6.3f} | Tot%:{row['pct_total']:+6.2f}% | D1%:{row['pct_day1']:+6.2f}% | Drift%:{row['pct_drift']:+6.2f}% | VolRatio:{row['vol_ratio']:5.2f}x")
