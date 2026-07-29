import urllib.request
import json
import time
import re
import yfinance as yf

HEADERS = {'User-Agent': 'MasonInvestments mason@example.com'}

def fetch_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read()
    except Exception as e:
        # print(f"Error fetching {url}: {e}")
        return None

def fetch_json(url):
    content = fetch_url(url)
    if content:
        try:
            return json.loads(content.decode('utf-8'))
        except Exception:
            return None
    return None

# Load company tickers mapping
print("Loading SEC company tickers...")
tickers_json = fetch_json("https://www.sec.gov/files/company_tickers.json")

ticker_to_cik = {}
cik_to_ticker = {}
if tickers_json:
    for k, v in tickers_json.items():
        t = v['ticker']
        c = str(v['cik_str']).zfill(10)
        ticker_to_cik[t] = c
        cik_to_ticker[c] = (t, v['title'])

print(f"Loaded {len(ticker_to_cik)} tickers.")

# Candidate pool search via EFTS
queries = [
    'robotics',
    'automation',
    '"industrial control"',
    'cobot',
    '"autonomous mobile robot"',
    '"motion control"',
    '"automated guided vehicle"'
]

candidate_ciks = set()

# Add seed PDYN
if 'PDYN' in ticker_to_cik:
    candidate_ciks.add(ticker_to_cik['PDYN'])

for q in queries:
    url = f"https://efts.sec.gov/LATEST/search-index?q={urllib.parse.quote(q)}&forms=8-K&startdt=2025-07-23&enddt=2026-07-23&size=100"
    res = fetch_json(url)
    if res and 'hits' in res and 'hits' in res['hits']:
        for hit in res['hits']['hits']:
            ciks = hit['_source'].get('ciks', [])
            for c in ciks:
                c_padded = str(c).zfill(10)
                candidate_ciks.add(c_padded)

print(f"Total unique CIK candidates from search: {len(candidate_ciks)}")

# Check market caps and SIC codes
qualified_companies = {}

for cik in list(candidate_ciks):
    if cik not in cik_to_ticker:
        continue
    ticker, comp_name = cik_to_ticker[cik]
    
    # Get Market Cap via yfinance
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is None:
            continue
        mc_m = mc / 1e6
        if 50.0 <= mc_m <= 500.0:
            qualified_companies[ticker] = {
                'cik': cik,
                'name': comp_name,
                'market_cap_m': mc_m,
                'source': 'Yahoo Finance fast_info'
            }
            print(f"QUALIFIED: {ticker} ({comp_name}) - ${mc_m:.2f}M")
    except Exception as e:
        pass

print(f"\nFound {len(qualified_companies)} qualified companies in $50M-$500M market cap range.")

