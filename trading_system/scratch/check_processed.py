import json

with open('scratch/processed_rows.json', 'r') as f:
    rows = json.load(f)

print(f"Total rows: {len(rows)}\n")

for i, r in enumerate(rows[:10]):
    print(f"Row {i+1}: {r['ticker']} | {r['company']} | {r['mcap']} | {r['fdate']} | {r['items']} | Judgment: {r['judgment']}")
    print(f"  Summary: {r['summary']}")
    if r['why']:
        print(f"  Why: {r['why']}")
    print(f"  URL: {r['url']}\n")
