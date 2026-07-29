"""
End-to-end pipeline for the verified 45-ticker dataset:
  1. For each ticker, fetch recent 8-K filings from EDGAR full-text search
  2. Fetch and parse full filing text
  3. Make content-based Yes/No judgment
  4. Pull Alpaca price/volume reaction data
  5. Classify INSTANT/GRADUAL/FLAT
  6. Save results for comparison script
"""

import os, json, time, re, random
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv('/home/mason/Trading/.env')
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')

HEADERS = {
    'User-Agent': 'ResearchBot/1.0 (mason@research.com)',
    'Accept-Encoding': 'gzip, deflate',
}

BIOTECH = ['VXRT','AVXL','IKT','CRBU','FATE','NMRA','CHRS','SGMT','AQST','AKBA','ANVS','MCRB','VNDA','KPTI','ENTA']
MINING  = ['SOWG','GORO','PZG','VGZ','IDR','USAU','WWR','XPL','URG','USGO','REE','AREC','TMRC','EU','LODE']
FINTECH = ['RM','MFIN','ONIT','AJX','PFX','BCIC','SCM','EARN','CHMI','CCAP','MITT','LDI','OFS','RC','KPLT']

# ---- Step 1: Get CIK for each ticker ----
def get_cik(ticker):
    """Lookup CIK from EDGAR company tickers JSON."""
    url = 'https://www.sec.gov/files/company_tickers.json'
    r = requests.get(url, headers=HEADERS, timeout=30)
    data = r.json()
    for entry in data.values():
        if entry['ticker'].upper() == ticker.upper():
            return str(entry['cik_str']).zfill(10)
    return None

# Cache CIK lookups
print("Loading EDGAR ticker-to-CIK mapping...")
cik_url = 'https://www.sec.gov/files/company_tickers.json'
cik_resp = requests.get(cik_url, headers=HEADERS, timeout=30)
cik_data = cik_resp.json()
ticker_to_cik = {}
ticker_to_name = {}
for entry in cik_data.values():
    t = entry['ticker'].upper()
    ticker_to_cik[t] = str(entry['cik_str']).zfill(10)
    ticker_to_name[t] = entry['title']

all_tickers = BIOTECH + MINING + FINTECH
missing_cik = [t for t in all_tickers if t not in ticker_to_cik]
if missing_cik:
    print(f"WARNING: No CIK found for: {missing_cik}")

# ---- Step 2: Fetch 8-K filing index for each ticker ----
def fetch_8k_filings(ticker, cik, max_filings=3):
    """Fetch recent 8-K filings from EDGAR for a given CIK."""
    cik_stripped = cik.lstrip('0')
    url = f'https://efts.sec.gov/LATEST/search-index?q=%228-K%22&dateRange=custom&startdt=2025-07-27&enddt=2026-07-27&forms=8-K&entityName={cik_stripped}'
    
    # Use the EDGAR filing API instead
    submissions_url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    try:
        r = requests.get(submissions_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ERROR fetching submissions for {ticker}: {e}")
        return []
    
    recent = data.get('filings', {}).get('recent', {})
    forms = recent.get('form', [])
    dates = recent.get('filingDate', [])
    accessions = recent.get('accessionNumber', [])
    primary_docs = recent.get('primaryDocument', [])
    
    filings = []
    cutoff = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    for i in range(len(forms)):
        if forms[i] in ('8-K', '8-K/A') and dates[i] >= cutoff:
            acc_formatted = accessions[i].replace('-', '')
            doc_url = f'https://www.sec.gov/Archives/edgar/data/{cik_stripped}/{acc_formatted}/{primary_docs[i]}'
            filings.append({
                'filing_date': dates[i],
                'form': forms[i],
                'url': doc_url,
                'accession': accessions[i]
            })
            if len(filings) >= max_filings:
                break
    
    return filings

# ---- Step 3: Fetch and parse filing text ----
def fetch_filing_text(url, max_chars=8000):
    """Fetch full text of an 8-K filing."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:max_chars]
    except Exception as e:
        return f"ERROR: {e}"

# ---- Step 4: Detect item types ----
def detect_items(text):
    items = []
    text_lower = text.lower()
    for item_num in ['1.01','1.02','2.01','2.02','2.03','3.01','3.02','3.03','4.01','4.02','5.01','5.02','5.03','5.07','7.01','8.01','9.01']:
        if f'item {item_num}' in text_lower or f'item\xa0{item_num}' in text_lower:
            items.append(f'Item {item_num}')
    if not items:
        items = ['Item 8.01']
    return items

# ---- Step 5: Content-based Yes/No judgment ----
def judge_filing(text, items, industry):
    text_lower = text.lower()
    items_str = ', '.join(items)
    
    # ---- BIOTECH ----
    if industry == 'Biotech':
        # Clinical data disclosure
        if any(k in text_lower for k in ['phase 1', 'phase 2', 'phase 3', 'primary endpoint', 
               'overall survival', 'progression-free', 'objective response rate',
               'clinical data', 'topline results', 'pivotal trial', 'interim analysis',
               'hazard ratio', 'p-value', 'statistically significant']):
            if any(k in text_lower for k in ['results', 'data', 'outcome', 'efficacy', 'response rate']):
                return 'Yes', 'Filing presents concrete clinical trial data disclosing therapeutic efficacy or endpoint performance.'
        
        # FDA action
        if any(k in text_lower for k in ['fda approval', 'fda accepted', 'complete response letter',
               'pdufa', 'breakthrough therapy', 'fast track', 'accelerated approval',
               'new drug application', 'biologics license', 'advisory committee']):
            return 'Yes', 'Filing discloses a specific FDA regulatory action, decision, or milestone.'
        
        # Material financing (dilutive offering)
        if 'Item 1.01' in items or any(k in text_lower for k in ['securities purchase agreement', 
               'registered direct', 'private placement', 'public offering', 'underwriting agreement']):
            if any(k in text_lower for k in ['gross proceeds', 'aggregate', 'shares of common', 'warrant']):
                return 'Yes', 'Filing details a concrete dilutive equity financing transaction specifying gross proceeds and share pricing.'
        
        # Licensing/partnership deal
        if any(k in text_lower for k in ['license agreement', 'collaboration agreement', 'milestone payment',
               'royalty', 'exclusive license', 'co-development']):
            if any(k in text_lower for k in ['upfront payment', 'milestone', 'total consideration']):
                return 'Yes', 'Filing discloses a material licensing or collaboration agreement with quantified financial terms.'
    
    # ---- MINING ----
    elif industry == 'Mining':
        # Drill results / assay data
        if any(k in text_lower for k in ['drill results', 'assay results', 'grams per tonne', 'g/t',
               'meters of', 'intercept', 'mineralization', 'ore grade', 'copper equivalent',
               'gold equivalent', 'resource estimate', 'mineral resource']):
            return 'Yes', 'Filing discloses drill assay results, resource estimates, or mineralization data.'
        
        # Permit / regulatory
        if any(k in text_lower for k in ['mining permit', 'environmental assessment', 'record of decision',
               'permit approved', 'permit denied', 'environmental impact']):
            return 'Yes', 'Filing discloses a mining permit decision or environmental regulatory action.'
        
        # Material acquisition / JV
        if any(k in text_lower for k in ['acquisition agreement', 'joint venture', 'option agreement',
               'property acquisition', 'mining lease']):
            if any(k in text_lower for k in ['consideration', 'purchase price', 'aggregate']):
                return 'Yes', 'Filing discloses a material property acquisition or joint venture agreement with financial terms.'
        
        # Production / operational milestone
        if any(k in text_lower for k in ['first pour', 'commercial production', 'production commenced',
               'processing plant', 'mill commissioning']):
            return 'Yes', 'Filing reports a major production milestone or operational achievement.'
    
    # ---- FINTECH ----
    elif industry == 'Fintech':
        # Credit facility / warehouse line
        if 'Item 1.01' in items or any(k in text_lower for k in ['credit agreement', 'revolving credit',
               'warehouse agreement', 'loan and security agreement', 'credit facility',
               'amendment to credit', 'securities purchase agreement']):
            if any(k in text_lower for k in ['commitment', 'aggregate', 'principal amount', 'interest rate',
                   'maturity', 'borrowing base', 'gross proceeds']):
                return 'Yes', 'Filing discloses a material credit facility agreement defining borrowing capacity and interest terms.'
        
        # Regulatory action
        if any(k in text_lower for k in ['consent order', 'enforcement action', 'cfpb', 'cease and desist',
               'civil money penalty', 'regulatory notice', 'supervisory agreement']):
            return 'Yes', 'Filing discloses a formal regulatory enforcement action or supervisory order.'
        
        # C-suite change (only CEO/CFO/President)
        if 'Item 5.02' in items:
            if any(k in text_lower for k in ['chief executive officer', 'chief financial officer', 'president']):
                if any(k in text_lower for k in ['resigned', 'appointed', 'terminated', 'departure',
                       'effective immediately', 'succeeded by']):
                    return 'Yes', 'Filing reports the resignation or appointment of C-suite executive leadership.'
        
        # Loan loss / credit quality
        if any(k in text_lower for k in ['provision for credit losses', 'charge-off', 'non-performing',
               'portfolio impairment', 'loan loss reserve', 'credit quality deterioration']):
            if any(k in text_lower for k in ['increase', 'material', 'significant', 'elevated']):
                return 'Yes', 'Filing discloses material credit quality deterioration or elevated loan loss provisions.'
    
    return 'No', ''

# ---- MAIN PIPELINE ----
all_filing_records = []

for industry, tickers in [('Biotech', BIOTECH), ('Mining', MINING), ('Fintech', FINTECH)]:
    print(f"\n{'='*60}")
    print(f"  Processing {industry} ({len(tickers)} tickers)")
    print(f"{'='*60}")
    
    for ticker in tickers:
        cik = ticker_to_cik.get(ticker)
        company = ticker_to_name.get(ticker, ticker)
        
        if not cik:
            print(f"  {ticker}: NO CIK FOUND — skipping")
            continue
        
        print(f"\n  {ticker} ({company}, CIK: {cik})...")
        filings = fetch_8k_filings(ticker, cik, max_filings=3)
        time.sleep(0.15)  # EDGAR rate limit
        
        if not filings:
            print(f"    No 8-K filings found in last 12 months")
            continue
        
        for fi in filings:
            print(f"    Fetching {fi['filing_date']} {fi['url'][:80]}...")
            text = fetch_filing_text(fi['url'])
            time.sleep(0.15)
            
            if text.startswith('ERROR'):
                print(f"      {text}")
                continue
            
            items = detect_items(text)
            judgment, why = judge_filing(text, items, industry)
            
            all_filing_records.append({
                'ticker': ticker,
                'company': company,
                'industry': industry,
                'filing_date': fi['filing_date'],
                'filing_url': fi['url'],
                'items': ', '.join(items),
                'judgment': judgment,
                'why': why,
                'text_snippet': text[:2000]
            })
            
            print(f"      Items: {', '.join(items)} | Judgment: {judgment}")

print(f"\n\nTotal filings fetched: {len(all_filing_records)}")
yes_count = sum(1 for r in all_filing_records if r['judgment'] == 'Yes')
no_count = sum(1 for r in all_filing_records if r['judgment'] == 'No')
print(f"Yes: {yes_count}, No: {no_count}")

# Save
with open('/home/mason/Trading/scratch/verified_45_filings.json', 'w') as f:
    json.dump(all_filing_records, f, indent=2)

print("\nSaved to scratch/verified_45_filings.json")

# ---- Step 6: Alpaca price/volume data ----
print("\n\n" + "="*60)
print("  Fetching Alpaca price data...")
print("="*60)

client = StockHistoricalDataClient(api_key, secret_key)
all_valid_tickers = sorted(list(set(r['ticker'] for r in all_filing_records)))

print(f"Fetching daily bars for {len(all_valid_tickers)} tickers...")
req = StockBarsRequest(
    symbol_or_symbols=all_valid_tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2025, 5, 1),
    end=datetime(2026, 7, 28),
    feed=DataFeed.IEX
)

bars_df = client.get_stock_bars(req).df.reset_index()
bars_df['date'] = pd.to_datetime(bars_df['timestamp']).dt.tz_localize(None).dt.normalize()
print(f"Total bars fetched: {len(bars_df)}")

# ---- Step 7: Classify reactions ----
results = []
insufficient = []

for f in all_filing_records:
    ticker = f['ticker']
    f_date = pd.to_datetime(f['filing_date']).normalize()
    
    t_bars = bars_df[bars_df['symbol'] == ticker].sort_values('date').reset_index(drop=True)
    
    if t_bars.empty:
        insufficient.append({'ticker': ticker, 'filing_date': f['filing_date'], 
                           'industry': f['industry'], 'judgment': f['judgment'],
                           'reason': 'No bar data at all'})
        continue
    
    t0_matches = t_bars[t_bars['date'] == f_date]
    if t0_matches.empty:
        insufficient.append({'ticker': ticker, 'filing_date': f['filing_date'],
                           'industry': f['industry'], 'judgment': f['judgment'],
                           'reason': 'Filing date not in bar data'})
        continue
    
    t0_idx = t0_matches.index[0]
    
    if t0_idx < 10:
        insufficient.append({'ticker': ticker, 'filing_date': f['filing_date'],
                           'industry': f['industry'], 'judgment': f['judgment'],
                           'reason': f'Fewer than 10 pre-days ({t0_idx})'})
        continue
    
    if t0_idx + 15 >= len(t_bars):
        avail_after = len(t_bars) - 1 - t0_idx
        insufficient.append({'ticker': ticker, 'filing_date': f['filing_date'],
                           'industry': f['industry'], 'judgment': f['judgment'],
                           'reason': f'Fewer than 15 post-days ({avail_after})'})
        continue
    
    bar_m10_to_m1 = t_bars.iloc[t0_idx-10:t0_idx]
    bar_m1 = t_bars.iloc[t0_idx-1]
    bar_0 = t_bars.iloc[t0_idx]
    bar_p1 = t_bars.iloc[t0_idx+1]
    bar_p5 = t_bars.iloc[t0_idx+5]
    bar_p15 = t_bars.iloc[t0_idx+15]
    bar_p1_to_p15 = t_bars.iloc[t0_idx+1:t0_idx+16]
    
    p_m1 = float(bar_m1['close'])
    p_0  = float(bar_0['close'])
    p_p1 = float(bar_p1['close'])
    p_p5 = float(bar_p5['close'])
    p_p15= float(bar_p15['close'])
    
    avg_vol_before = float(bar_m10_to_m1['volume'].mean())
    avg_vol_after  = float(bar_p1_to_p15['volume'].mean())
    vol_ratio = avg_vol_after / avg_vol_before if avg_vol_before > 0 else 0.0
    
    pct_total = (p_p15 - p_m1) / p_m1 * 100.0
    pct_5d    = (p_p5 - p_m1) / p_m1 * 100.0
    pct_day1  = (p_p1 - p_m1) / p_m1 * 100.0
    pct_drift = (p_p15 - p_p1) / p_m1 * 100.0
    
    abs_tot = abs(pct_total)
    abs_5d  = abs(pct_5d)
    abs_d1  = abs(pct_day1)
    frac_day1 = pct_day1 / pct_total if pct_total != 0 else 0
    
    if abs_tot < 4.0:
        classification = "FLAT/NONE"
    elif (frac_day1 >= 0.60 and abs(pct_drift) <= max(3.5, 0.4 * abs_d1)) or \
         (abs_d1 >= 10.0 and frac_day1 >= 0.50 and abs(pct_drift) <= 0.5 * abs_d1):
        classification = "INSTANT"
    else:
        classification = "GRADUAL"
    
    flagged = (vol_ratio > 2.0) and (classification == "GRADUAL")
    vol_spike_2x = (vol_ratio > 2.0)
    
    results.append({
        'ticker': ticker,
        'company': f['company'],
        'industry': f['industry'],
        'filing_date': f['filing_date'],
        'plausible': f['judgment'],
        'why': f['why'],
        'items': f['items'],
        'p_m1': p_m1, 'p_0': p_0, 'p_p1': p_p1, 'p_p5': p_p5, 'p_p15': p_p15,
        'avg_vol_before': avg_vol_before,
        'avg_vol_after': avg_vol_after,
        'vol_ratio': vol_ratio,
        'pct_1d': pct_day1, 'pct_5d': pct_5d, 'pct_15d': pct_total,
        'abs_1d': abs_d1, 'abs_5d': abs_5d, 'abs_15d': abs_tot,
        'classification': classification,
        'flagged': flagged,
        'vol_spike_2x': vol_spike_2x
    })

df_results = pd.DataFrame(results)
df_insuf = pd.DataFrame(insufficient)

print(f"\nValid results: {len(df_results)}")
print(f"Insufficient data: {len(df_insuf)}")

if len(df_insuf) > 0:
    print("\nInsufficient data details:")
    for _, row in df_insuf.iterrows():
        print(f"  {row['ticker']} ({row['industry']}) {row['filing_date']}: {row['reason']}")

# Save
df_results.to_csv('/home/mason/Trading/scratch/verified_45_results.csv', index=False)
if len(df_insuf) > 0:
    df_insuf.to_csv('/home/mason/Trading/scratch/verified_45_insufficient.csv', index=False)

print(f"\n\nFinal breakdown:")
yes_valid = df_results[df_results['plausible'] == 'Yes']
no_valid = df_results[df_results['plausible'] == 'No']
print(f"  YES valid: {len(yes_valid)} (Bio: {sum(yes_valid['industry']=='Biotech')}, Min: {sum(yes_valid['industry']=='Mining')}, Fin: {sum(yes_valid['industry']=='Fintech')})")
print(f"  NO  valid: {len(no_valid)} (Bio: {sum(no_valid['industry']=='Biotech')}, Min: {sum(no_valid['industry']=='Mining')}, Fin: {sum(no_valid['industry']=='Fintech')})")
print("\nDONE — data ready for comparison script")
