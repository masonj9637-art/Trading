import urllib.request
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
        # print(f"Error fetching {url}: {e}")
        return None

def fetch_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

# Selected Industrial Automation & Robotics Companies verified in $50M - $500M market cap range:
target_companies = {
    'PDYN': {'cik': '0001826681', 'name': 'Palladyne AI Corp.'},
    'SERV': {'cik': '0001832483', 'name': 'Serve Robotics Inc.'},
    'RR':   {'cik': '0001963685', 'name': 'Richtech Robotics Inc.'},
    'HURC': {'cik': '0000769520', 'name': 'Hurco Companies, Inc.'},
    'MBOT': {'cik': '0000883975', 'name': 'Microbot Medical Inc.'},
    'CLPT': {'cik': '0001285550', 'name': 'ClearPoint Neuro, Inc.'},
    'MGRM': {'cik': '0001769752', 'name': 'Monogram Technologies Inc.'},
    'SOTK': {'cik': '0000825514', 'name': 'Sono-Tek Corp'},
    'CMCO': {'cik': '0000022444', 'name': 'Columbus McKinnon Corp'},
    'RPID': {'cik': '0001833079', 'name': 'Rapid Micro Biosystems, Inc.'},
    'AMCI': {'cik': '0001937891', 'name': 'AMC Robotics Corp'},
    'XTIA': {'cik': '0001529113', 'name': 'XTI Aerospace, Inc.'}
}

# Verify market caps and fetch submission 8-Ks
all_filings = []

print("Gathering market caps and 8-Ks from last 12 months (2025-07-23 to 2026-07-23)...")

for ticker, info in target_companies.items():
    cik = info['cik']
    name = info['name']
    
    # Check yfinance market cap
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is None:
            print(f"Skipping {ticker}: no market cap")
            continue
        mc_m = mc / 1e6
        if not (50.0 <= mc_m <= 500.0):
            print(f"Skipping {ticker}: market cap ${mc_m:.1f}M outside $50M-$500M")
            continue
        mc_str = f"${mc_m:.1f}M (Yahoo Finance)"
    except Exception as e:
        print(f"Error checking market cap for {ticker}: {e}")
        continue
    
    # Fetch submissions JSON from SEC
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    sub_data = fetch_json(url)
    time.sleep(0.12) # Respect < 10 req/sec limit
    
    if not sub_data:
        print(f"Could not fetch submissions for {ticker}")
        continue
    
    recent = sub_data.get('filings', {}).get('recent', {})
    forms = recent.get('form', [])
    filing_dates = recent.get('filingDate', [])
    accessions = recent.get('accessionNumber', [])
    primary_docs = recent.get('primaryDocument', [])
    items_list = recent.get('items', [])
    doc_descs = recent.get('primaryDocDescription', [])
    
    cik_num = str(int(cik))
    
    for i in range(len(forms)):
        form = forms[i]
        fdate = filing_dates[i]
        
        # Check if 8-K and within last 12 months (2025-07-23 to 2026-07-23)
        if form in ['8-K', '8-K/A'] and '2025-07-23' <= fdate <= '2026-07-23':
            acc_num = accessions[i]
            acc_no_hyphen = acc_num.replace('-', '')
            primary_doc = primary_docs[i]
            items = items_list[i] if i < len(items_list) else ""
            
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_no_hyphen}/{primary_doc}"
            
            # Fetch brief doc snippet to extract factual disclosure description
            doc_text = fetch_text(doc_url)
            time.sleep(0.12)
            
            desc = ""
            if doc_text:
                # Clean HTML tags to text
                clean_text = re.sub(r'<[^>]+>', ' ', doc_text[:15000])
                clean_text = ' '.join(clean_text.split())
                
                # Check for Item titles or headline in press release / 8-K body
                # Look for specific contract dollar amounts, officer changes, earnings, financing, etc.
                match_contract = re.search(r'(\$[\d\.]+\s*(?:million|M|billion|B)?\s*(?:contract|award|purchase order|agreement))', clean_text, re.IGNORECASE)
                match_item = re.search(r'Item\s+([\d\.]+)\s*([^\.]{5,100})', clean_text, re.IGNORECASE)
                
                if 'Item 1.01' in clean_text or 'Item 1.01' in str(items):
                    desc = "Discloses entry into a material definitive agreement."
                    if match_contract:
                        desc = f"Discloses entry into material agreement regarding {match_contract.group(1)}."
                elif 'Item 2.02' in clean_text or 'Item 2.02' in str(items):
                    desc = "Discloses financial results and operating updates."
                elif 'Item 5.02' in clean_text or 'Item 5.02' in str(items):
                    desc = "Discloses changes in directors or principal officers."
                elif 'Item 3.02' in clean_text or 'Item 3.02' in str(items):
                    desc = "Discloses unregistered sales of equity securities."
                elif 'Item 8.01' in clean_text or 'Item 8.01' in str(items):
                    desc = "Discloses other material corporate events and press release updates."
                elif 'Item 5.07' in clean_text or 'Item 5.07' in str(items):
                    desc = "Discloses submission of matters to a vote of security holders."
                elif 'Item 1.02' in clean_text or 'Item 1.02' in str(items):
                    desc = "Discloses termination of a material definitive agreement."
                else:
                    desc = "Discloses material corporate developments under Form 8-K."
            else:
                desc = "Discloses material corporate events under Form 8-K."
            
            all_filings.append({
                'ticker': ticker,
                'name': name,
                'market_cap': mc_str,
                'form': form,
                'date': fdate,
                'url': doc_url,
                'description': desc
            })

print(f"\nTotal 8-K filings collected: {len(all_filings)}")

# Sort descending by filing date
all_filings.sort(key=lambda x: x['date'], reverse=True)

for f in all_filings[:15]:
    print(f['date'], f['ticker'], f['form'], f['description'])

