import urllib.request
import json
import time
import yfinance as yf

HEADERS = {'User-Agent': 'MasonInvestments mason@example.com'}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def search_efts(query, start_dt="2025-07-23", end_dt="2026-07-23", size=100, from_idx=0):
    url = f"https://efts.sec.gov/LATEST/search-index?q={urllib.parse.quote(query)}&forms=8-K&startdt={start_dt}&enddt={end_dt}&size={size}&from={from_idx}"
    return fetch_json(url)

# Test candidate queries
queries = [
    'robotics',
    'automation',
    'autonomous',
    '"industrial control"',
    'cobot',
    '"industrial robot"'
]

candidates = {}

for q in queries:
    res = search_efts(q, size=100)
    if res and 'hits' in res and 'hits' in res['hits']:
        for hit in res['hits']['hits']:
            src = hit['_source']
            ciks = src.get('ciks', [])
            names = src.get('display_names', [])
            sics = src.get('sics', [])
            if names:
                name_str = names[0]
                # parse ticker if present e.g. "Palladyne AI Corp. (PDYN) (CIK 0001826681)"
                ticker = None
                if '(' in name_str and ')' in name_str:
                    parts = name_str.split('(')
                    for p in parts[1:]:
                        clean_p = p.split(')')[0].strip()
                        if clean_p.isupper() and 1 <= len(clean_p) <= 5 and not clean_p.startswith('CIK'):
                            ticker = clean_p
                            break
                if ticker and ticker not in candidates:
                    candidates[ticker] = {
                        'name': name_str,
                        'cik': ciks[0] if ciks else None,
                        'sics': sics
                    }

print(f"Found {len(candidates)} total distinct candidate tickers.")
for t, info in list(candidates.items())[:30]:
    print(t, info['name'][:50])

