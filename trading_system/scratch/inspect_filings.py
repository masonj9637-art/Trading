import json
import re

with open('scratch/parsed_8k_filings.json', 'r') as f:
    filings = json.load(f)

print(f"Loaded {len(filings)} filings.")

# Helper to examine filing text snippet
for idx, f in enumerate(filings[:15]):
    print(f"--- Filing {idx+1}: {f['ticker']} ({f['filing_date']}) ---")
    print(f"URL: {f['filing_url']}")
    text = f['text_snippet']
    # Print first 500 chars of text snippet
    print(text[:500].replace('\n', ' '))
    print()

