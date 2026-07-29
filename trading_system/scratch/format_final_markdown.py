import json

with open('scratch/final_biotech_rows.json', 'r') as f:
    rows = json.load(f)

md_lines = []
md_lines.append("# SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies\n")
md_lines.append("## Executive Summary\n")
md_lines.append(f"- **Screening Criteria**: Small-Cap ($50M – $500M market cap), SIC Codes 2836 / 8731 / 2834 or keyword search ('clinical trial', 'FDA', 'biopharmaceutical')")
md_lines.append(f"- **Filing Window**: Last 12 Months (July 23, 2025 – July 23, 2026)")
md_lines.append(f"- **Total 8-K Filings Full-Text Reviewed**: {len(rows)}")
md_lines.append(f"- **Plausible Price-Moving Content (Yes)**: {sum(1 for r in rows if r['judgment']=='Yes')}")
md_lines.append(f"- **Routine Disclosures (No)**: {sum(1 for r in rows if r['judgment']=='No')}\n")
md_lines.append("---\n")

md_lines.append("## Detailed SEC 8-K Filings Analysis\n")
md_lines.append("| Ticker | Company | Market Cap | Filing Date | Filing URL | Item Type(s) | Summary of Actual Disclosed Content | Plausible Price Mover? | Reason (If Yes) |")
md_lines.append("|---|---|---|---|---|---|---|---|---|")

for r in rows:
    ticker = r['ticker']
    company = r['company']
    mcap = r['mcap']
    fdate = r['fdate']
    url = f"[{r['url'].split('/')[-1]}]({r['url']})"
    items = r['items']
    summary = r['summary'].replace('|', '-')
    judgment = r['judgment']
    why = r['why'].replace('|', '-') if r['why'] else "-"
    
    md_lines.append(f"| {ticker} | {company} | {mcap} | {fdate} | {url} | {items} | {summary} | **{judgment}** | {why} |")

with open('scratch/biotech_8k_review.md', 'w') as f:
    f.write("\n".join(md_lines))

print("Wrote scratch/biotech_8k_review.md successfully.")
