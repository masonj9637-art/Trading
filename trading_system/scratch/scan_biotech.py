import urllib.request
import urllib.parse
import json
import time
import re
import yfinance as yf

HEADERS = {'User-Agent': 'MasonInvestments mason@example.com'}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching JSON {url}: {e}")
        return None

def fetch_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching text {url}: {e}")
        return None

def search_efts(query=None, sic=None, start_dt="2025-07-23", end_dt="2026-07-23", size=100, from_idx=0):
    url = f"https://efts.sec.gov/LATEST/search-index?forms=8-K&startdt={start_dt}&enddt={end_dt}&size={size}&from={from_idx}"
    if query:
        url += f"&q={urllib.parse.quote(query)}"
    if sic:
        url += f"&sics={sic}"
    return fetch_json(url)

print("Searching SEC EFTS for biotech/pharma candidates...")

candidates = {} # ticker -> {cik, name, sic}

queries = [
    '"clinical trial"',
    '"FDA"',
    '"biopharmaceutical"',
    'Phase 1 OR Phase 2 OR Phase 3',
]

sics = ['2836', '8731', '2834']

# Search by SIC
for s in sics:
    print(f"Searching SIC {s}...")
    for offset in [0, 100, 200]:
        res = search_efts(sic=s, size=100, from_idx=offset)
        time.sleep(0.15)
        if res and 'hits' in res and 'hits' in res['hits']:
            hits = res['hits']['hits']
            print(f"  Got {len(hits)} hits for SIC {s} offset {offset}")
            for h in hits:
                src = h['_source']
                ciks = src.get('ciks', [])
                names = src.get('display_names', [])
                sic_list = src.get('sics', [])
                if names and ciks:
                    name_str = names[0]
                    # Parse ticker if available
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
                            'name': name_str.split('(')[0].strip(),
                            'cik': ciks[0].zfill(10),
                            'sic': sic_list[0] if sic_list else s
                        }

# Search by Keywords
for q in queries:
    print(f"Searching Query {q}...")
    for offset in [0, 100]:
        res = search_efts(query=q, size=100, from_idx=offset)
        time.sleep(0.15)
        if res and 'hits' in res and 'hits' in res['hits']:
            hits = res['hits']['hits']
            print(f"  Got {len(hits)} hits for query {q} offset {offset}")
            for h in hits:
                src = h['_source']
                ciks = src.get('ciks', [])
                names = src.get('display_names', [])
                sic_list = src.get('sics', [])
                if names and ciks:
                    name_str = names[0]
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
                            'name': name_str.split('(')[0].strip(),
                            'cik': ciks[0].zfill(10),
                            'sic': sic_list[0] if sic_list else ""
                        }

print(f"\nTotal candidate tickers found: {len(candidates)}")

# Now filter by Market Cap ($50M - $500M)
valid_biotech_companies = {}

print("\nFiltering companies by Market Cap ($50M - $500M)...")
for ticker, info in candidates.items():
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is None or mc == 0:
            # try info
            mc = t_obj.info.get('marketCap', None)
        if mc is None:
            continue
        mc_m = mc / 1e6
        if 50.0 <= mc_m <= 500.0:
            print(f"MATCH: {ticker} ({info['name']}) - Market Cap: ${mc_m:.1f}M")
            valid_biotech_companies[ticker] = {
                'name': info['name'],
                'cik': info['cik'],
                'market_cap': f"${mc_m:.1f}M",
                'mc_val': mc_m
            }
        else:
            # print(f"Skip {ticker}: ${mc_m:.1f}M")
            pass
    except Exception as e:
        # print(f"Error checking {ticker}: {e}")
        pass
    time.sleep(0.05)

print(f"\nTotal valid small-cap biotech companies ($50M-$500M): {len(valid_biotech_companies)}")

with open('scratch/valid_biotech_companies.json', 'w') as f:
    json.dump(valid_biotech_companies, f, indent=2)

