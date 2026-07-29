import urllib.request
import json
import time
import re
from bs4 import BeautifulSoup

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

def clean_html(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    # remove script and style elements
    for script in soup(["script", "style", "table"]):
        script.extract()
    text = soup.get_text(separator=' ')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

with open('scratch/valid_biotech_companies.json', 'r') as f:
    companies = json.load(f)

print(f"Loaded {len(companies)} valid biotech companies.")

# Select a representative set of 20 diverse biotech companies to fetch filings from
selected_tickers = [
    'VXRT', 'AVXL', 'IKT', 'CRDF', 'ENTX', 'AGEN', 'VYGR', 'OCGN', 
    'KYTX', 'ALEC', 'LENZ', 'TNYA', 'XFOR', 'CMPX', 'AUTL', 'EDIT', 
    'CRBU', 'FATE', 'NMRA', 'CHRS', 'SGMT', 'AQST', 'AKBA', 'ANVS'
]

results = []

for ticker in selected_tickers:
    if ticker not in companies:
        continue
    info = companies[ticker]
    cik = info['cik']
    name = info['name']
    mcap = info['market_cap']
    
    print(f"\nFetching 8-Ks for {ticker} ({name}, CIK: {cik})...")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    sub_data = fetch_json(url)
    time.sleep(0.12)
    
    if not sub_data:
        continue
    
    recent = sub_data.get('filings', {}).get('recent', {})
    forms = recent.get('form', [])
    filing_dates = recent.get('filingDate', [])
    accessions = recent.get('accessionNumber', [])
    primary_docs = recent.get('primaryDocument', [])
    items_list = recent.get('items', [])
    
    cik_num = str(int(cik))
    
    company_filings_count = 0
    for i in range(len(forms)):
        form = forms[i]
        fdate = filing_dates[i]
        
        if form in ['8-K', '8-K/A'] and '2025-07-23' <= fdate <= '2026-07-23':
            acc_num = accessions[i]
            acc_no_hyphen = acc_num.replace('-', '')
            primary_doc = primary_docs[i]
            items = items_list[i] if i < len(items_list) else ""
            
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_no_hyphen}/{primary_doc}"
            
            print(f"  Fetching filing text {fdate} {doc_url}...")
            raw_text = fetch_text(doc_url)
            time.sleep(0.12)
            
            cleaned_text = clean_html(raw_text)
            
            results.append({
                'ticker': ticker,
                'company': name,
                'market_cap': mcap,
                'filing_date': fdate,
                'filing_url': doc_url,
                'items_raw': items,
                'text_snippet': cleaned_text[:4000]
            })
            company_filings_count += 1
            if company_filings_count >= 3: # limit to max 3 filings per company to keep dataset balanced
                break

print(f"\nTotal filings fetched and parsed: {len(results)}")

with open('scratch/parsed_8k_filings.json', 'w') as f:
    json.dump(results, f, indent=2)

