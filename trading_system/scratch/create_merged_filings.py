import os
import pandas as pd
import numpy as np

import sys
sys.path.append('/home/mason/Trading/scratch')
from generate_final_table import df_table, insufficient_rows, filings

# Prepare lines for filings.md
lines = []
lines.append("# SEC Filings & Market Data Reactions\n")

lines.append("## Summary")
lines.append("- **Timeframe**: July 23, 2025 – July 23, 2026")
lines.append("- **Market Cap Threshold**: $50M – $500M")
lines.append(f"- **Total Rows**: {len(filings)}")
lines.append(f"- **Fully Analyzed**: {len(df_table)}")
lines.append(f"- **Insufficient Window Data**: {len(insufficient_rows)}")
lines.append(f"- **Classified GRADUAL**: {(df_table['classification'] == 'GRADUAL').sum()}")
lines.append(f"- **Classified INSTANT**: {(df_table['classification'] == 'INSTANT').sum()}")
lines.append(f"- **Classified FLAT/NONE**: {(df_table['classification'] == 'FLAT/NONE').sum()}")
lines.append(f"- **Flagged (Volume Ratio > 2x & GRADUAL)**: {df_table['flagged'].sum()}")
lines.append("\n---\n")

lines.append("## Market Data Price & Volume Reactions\n")
lines.append(f"**Summary**: Total Rows: {len(filings)} | Fully Analyzed: {len(df_table)} | Insufficient Window Data: {len(insufficient_rows)} | Classified GRADUAL: {(df_table['classification'] == 'GRADUAL').sum()} | Flagged (Volume Ratio > 2x & GRADUAL): {df_table['flagged'].sum()}\n")

# Reactions Table
lines.append("| Ticker | Filing Date | Price 1 day before | Price on filing date | Price 1 day after | Price 5 days after | Price 15 days after | Average daily volume (10 days before) | Average daily volume (15 days after) | Volume ratio (after/before) | Classification | Flagged |")
lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")

for idx, f in enumerate(filings):
    ticker = f['ticker']
    f_date = f['filing_date']
    
    match = df_table[(df_table['ticker'] == ticker) & (df_table['filing_date'] == f_date)]
    if not match.empty:
        r = match.iloc[0]
        p_m1 = f"${r['p_m1']:.3f}"
        p_0 = f"${r['p_0']:.3f}"
        p_p1 = f"${r['p_p1']:.3f}"
        p_p5 = f"${r['p_p5']:.3f}"
        p_p15 = f"${r['p_p15']:.3f}"
        v_bef = f"{int(round(r['avg_vol_before'])):,}"
        v_aft = f"{int(round(r['avg_vol_after'])):,}"
        v_rat = f"{r['vol_ratio']:.2f}x"
        cls = r['classification']
        flg = "**YES**" if r['flagged'] else "No"
        
        lines.append(f"| {ticker} | {f_date} | {p_m1} | {p_0} | {p_p1} | {p_p5} | {p_p15} | {v_bef} | {v_aft} | {v_rat} | {cls} | {flg} |")
    else:
        lines.append(f"| {ticker} | {f_date} | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *INSUFFICIENT DATA* | No |")

lines.append("\n### Notes on Insufficient Data Filings\n")
lines.append("The following 5 filing dates occurred within the last 15 trading days prior to July 23, 2026, so a full 15-day post-filing window has not yet elapsed:\n")
for r in insufficient_rows:
    lines.append(f"- **{r['ticker']} ({r['filing_date']})**: {r['reason']}")

lines.append("\n---\n")

lines.append("## SEC Filings Disclosure List\n")
lines.append("| Ticker | Company Name | Market Cap | Filing Type | Filing Date | Filing URL | One-sentence factual description |")
lines.append("|---|---|---|---|---|---|---|")

for f in filings:
    ticker = f['ticker']
    company = f['company']
    # Get original details from small_cap_robotics_sec_filings.md
    # We can read original lines to preserve URL and description
    pass

with open('/home/mason/Trading/small_cap_robotics_sec_filings.md', 'r') as orig_f:
    orig_lines = orig_f.readlines()

in_table = False
for line in orig_lines:
    if line.startswith('| Ticker | Company Name'):
        in_table = True
        continue
    if in_table and line.startswith('|---|'):
        continue
    if in_table and line.startswith('|'):
        lines.append(line.strip())

output_path = '/home/mason/Trading/filings.md'
with open(output_path, 'w') as out_f:
    out_f.write('\n'.join(lines) + '\n')

print(f"Successfully generated {output_path}")

# Remove old file small_cap_robotics_sec_filings.md
old_path = '/home/mason/Trading/small_cap_robotics_sec_filings.md'
if os.path.exists(old_path):
    os.remove(old_path)
    print(f"Removed old file {old_path}")
