import sys
sys.path.append('/home/mason/Trading/scratch')
from generate_final_table import df_table, insufficient_rows, filings

markdown_output = []

# Top Summary Line
total_rows = len(filings)
total_analyzed = len(df_table)
total_insufficient = len(insufficient_rows)
gradual_count = (df_table['classification'] == 'GRADUAL').sum()
flagged_count = df_table['flagged'].sum()

summary_line = f"**Summary**: Total Rows: {total_rows} | Fully Analyzed: {total_analyzed} | Insufficient Window Data: {total_insufficient} | Classified GRADUAL: {gradual_count} | Flagged (Volume Ratio > 2x & GRADUAL): {flagged_count}"
print(summary_line)
print("\n")

# Main Table Header
header = "| Ticker | Filing Date | Price 1 day before | Price on filing date | Price 1 day after | Price 5 days after | Price 15 days after | Average daily volume (10 days before) | Average daily volume (15 days after) | Volume ratio (after/before) | Classification | Flagged |"
separator = "|---|---|---|---|---|---|---|---|---|---|---|---|"

print(header)
print(separator)

for idx, f in enumerate(filings):
    row_num = idx + 1
    ticker = f['ticker']
    f_date = f['filing_date']
    
    # Check if in df_table
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
        
        row_str = f"| {ticker} | {f_date} | {p_m1} | {p_0} | {p_p1} | {p_p5} | {p_p15} | {v_bef} | {v_aft} | {v_rat} | {cls} | {flg} |"
        print(row_str)
    else:
        # Find reason in insufficient_rows
        reason_match = [ir for ir in insufficient_rows if ir['ticker'] == ticker and ir['filing_date'] == f_date]
        reason = reason_match[0]['reason'] if reason_match else "Data unavailable"
        row_str = f"| {ticker} | {f_date} | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *N/A* | *INSUFFICIENT DATA* | No |"
        print(row_str)
