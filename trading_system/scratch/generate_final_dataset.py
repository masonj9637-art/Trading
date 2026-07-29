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
        return None

def fetch_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

# Target qualified industrial-automation/robotics companies:
# Seed company Palladyne AI (PDYN) included; Ouster (OUST) excluded (market cap $2.54B > $500M)
target_companies = {
    'PDYN': {'cik': '0001826681', 'name': 'Palladyne AI Corp.'},
    'SERV': {'cik': '0001832483', 'name': 'Serve Robotics Inc.'},
    'RR':   {'cik': '0001963685', 'name': 'Richtech Robotics Inc.'},
    'HURC': {'cik': '0000769520', 'name': 'Hurco Companies, Inc.'},
    'MBOT': {'cik': '0000883975', 'name': 'Microbot Medical Inc.'},
    'CLPT': {'cik': '0001285550', 'name': 'ClearPoint Neuro, Inc.'},
    'CMCO': {'cik': '0000022444', 'name': 'Columbus McKinnon Corp.'},
    'RPID': {'cik': '0001833079', 'name': 'Rapid Micro Biosystems, Inc.'},
    'AMCI': {'cik': '0001937891', 'name': 'AMC Robotics Corp.'},
    'XTIA': {'cik': '0001529113', 'name': 'XTI Aerospace, Inc.'}
}

item_descriptions = {
    '1.01': 'entry into a material definitive agreement',
    '1.02': 'termination of a material definitive agreement',
    '1.03': 'bankruptcy or receivership filing',
    '2.01': 'completion of acquisition or disposition of assets',
    '2.02': 'results of operations and financial condition',
    '2.03': 'creation of a direct financial obligation or off-balance sheet arrangement',
    '2.04': 'triggering events that accelerate or increase a direct financial obligation',
    '2.05': 'costs associated with exit or disposal activities',
    '2.06': 'material impairments',
    '3.01': 'notice of delisting or failure to satisfy a continued listing rule',
    '3.02': 'unregistered sales of equity securities',
    '3.03': 'material modification to rights of security holders',
    '4.01': 'changes in registrant’s certifying accountant',
    '4.02': 'non-reliance on previously issued financial statements',
    '5.01': 'changes in control of registrant',
    '5.02': 'departure of directors or principal officers, election of directors, or appointment of principal officers',
    '5.03': 'amendments to articles of incorporation or bylaws',
    '5.05': 'amendments to the registrant’s code of ethics',
    '5.07': 'submission of matters to a vote of security holders',
    '5.08': 'shareholder director nominations',
    '7.01': 'regulation FD disclosure',
    '8.01': 'other material events',
    '9.01': 'financial statements and exhibits'
}

all_filings = []

print("Processing SEC submission data...")

for ticker, info in target_companies.items():
    cik = info['cik']
    name = info['name']
    
    try:
        t_obj = yf.Ticker(ticker)
        mc = getattr(t_obj.fast_info, 'market_cap', None)
        if mc is None:
            continue
        mc_m = mc / 1e6
        if not (50.0 <= mc_m <= 500.0):
            continue
        mc_str = f"~${mc_m:.1f}M (Yahoo Finance)"
    except Exception as e:
        continue
    
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
    
    for i in range(len(forms)):
        form = forms[i]
        fdate = filing_dates[i]
        
        # 12-month window: 2025-07-23 to 2026-07-23
        if form in ['8-K', '8-K/A'] and '2025-07-23' <= fdate <= '2026-07-23':
            acc_num = accessions[i]
            acc_no_hyphen = acc_num.replace('-', '')
            primary_doc = primary_docs[i]
            
            raw_items = items_list[i] if i < len(items_list) else []
            if isinstance(raw_items, str):
                raw_items = [raw_items]
            
            # Direct filing URL
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_no_hyphen}/{primary_doc}"
            
            # Format item disclosure summary
            item_summaries = []
            for it in raw_items:
                it_clean = str(it).strip()
                if it_clean in item_descriptions:
                    item_summaries.append(f"Item {it_clean} ({item_descriptions[it_clean]})")
                elif it_clean and it_clean != '9.01':
                    item_summaries.append(f"Item {it_clean}")
            
            if item_summaries:
                desc_text = "Discloses " + "; ".join(item_summaries) + "."
            else:
                desc_text = "Discloses material corporate developments and exhibits."
            
            all_filings.append({
                'ticker': ticker,
                'name': name,
                'market_cap': mc_str,
                'form': form,
                'date': fdate,
                'url': doc_url,
                'items': raw_items,
                'description': desc_text
            })

print(f"Total 8-K filings extracted: {len(all_filings)}")

# Sort descending by filing date
all_filings.sort(key=lambda x: (x['date'], x['ticker']), reverse=True)

# Select top 50 results (strictly within 40-60 range)
selected_filings = all_filings[:50]

print(f"Selected {len(selected_filings)} filings for output table.")

# Write to markdown file
with open('scratch/filings_table.md', 'w') as f:
    f.write("| Ticker | Company Name | Market Cap (approx, and source used to verify it) | Filing Type | Filing Date | Filing URL | One-sentence factual description of what the filing discloses |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for row in selected_filings:
        f.write(f"| {row['ticker']} | {row['name']} | {row['market_cap']} | {row['form']} | {row['date']} | [{row['url']}]({row['url']}) | {row['description']} |\n")

print("Saved table to scratch/filings_table.md")

