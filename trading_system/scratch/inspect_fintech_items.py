import json

with open('scratch/parsed_fintech_8k_filings.json', 'r') as f:
    filings = json.load(f)

for idx, f in enumerate(filings):
    text = f['text_snippet'].lower()
    items = f['items_raw']
    print(f"[{idx+1}] {f['ticker']} ({f['filing_date']}) - Items raw: '{items}'")
    if '1.01' in items or 'item 1.01' in text:
        print(f"  -> Has Item 1.01! Text snippet: {f['text_snippet'][:300].replace('\n', ' ')}")
    if '5.02' in items or 'item 5.02' in text:
        print(f"  -> Has Item 5.02! Text snippet: {f['text_snippet'][:300].replace('\n', ' ')}")
