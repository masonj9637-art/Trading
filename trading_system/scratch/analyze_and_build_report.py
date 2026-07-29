import json
import re

with open('scratch/parsed_8k_filings.json', 'r') as f:
    filings = json.load(f)

def analyze_single_filing(f):
    text = f['text_snippet']
    ticker = f['ticker']
    company = f['company']
    mcap = f['market_cap']
    fdate = f['filing_date']
    url = f['filing_url']
    raw_items = f['items_raw']
    
    # Identify Item types from text if raw_items is empty or needs refinement
    items_found = []
    item_matches = re.findall(r'Item\s+([1-9]\.[0-9]{2})', text, re.IGNORECASE)
    if item_matches:
        # unique preserved order
        for im in item_matches:
            formatted_item = f"Item {im}"
            if formatted_item not in items_found:
                items_found.append(formatted_item)
    
    if not items_found and raw_items:
        items_found = [f"Item {i.strip()}" for i in raw_items.split(',') if i.strip()]
        
    item_str = ", ".join(items_found) if items_found else "Item 8.01 (Other Events)"

    return {
        'ticker': ticker,
        'company': company,
        'market_cap': mcap,
        'filing_date': fdate,
        'filing_url': url,
        'item_types': item_str,
        'full_text': text
    }

analyzed_filings = [analyze_single_filing(f) for f in filings]

with open('scratch/filings_for_review.json', 'w') as f:
    json.dump(analyzed_filings, f, indent=2)

print(f"Prepared {len(analyzed_filings)} filings for detailed content review.")
