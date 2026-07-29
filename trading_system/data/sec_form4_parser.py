import requests
import xml.etree.ElementTree as ET
import re
import time
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

SEC_HEADERS = {
    'User-Agent': 'QuantResearch research@tradingbot.com'
}

class SECForm4Parser:
    def __init__(self, cache_dir='data'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.tickers_map_file = os.path.join(cache_dir, 'sec_tickers_map.json')
        self.clusters_cache_file = os.path.join(cache_dir, 'insider_clusters_cache.json')
        self.buys_cache_file = os.path.join(cache_dir, 'insider_buys_cache.json')

    def get_sec_ticker_map(self) -> dict:
        """
        Downloads or loads SEC CIK-to-Ticker mapping from data.sec.gov.
        Returns a dict mapping ticker -> CIK (str) and CIK -> ticker.
        """
        if os.path.exists(self.tickers_map_file):
            with open(self.tickers_map_file, 'r') as f:
                return json.load(f)
        
        url = 'https://www.sec.gov/files/company_tickers.json'
        r = requests.get(url, headers=SEC_HEADERS)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch SEC ticker map: HTTP {r.status_code}")
            
        data = r.json()
        ticker_to_cik = {}
        cik_to_ticker = {}
        for entry in data.values():
            sym = str(entry['ticker']).upper()
            cik = str(entry['cik_str']).zfill(10)
            ticker_to_cik[sym] = cik
            cik_to_ticker[cik] = sym
            
        res = {'ticker_to_cik': ticker_to_cik, 'cik_to_ticker': cik_to_ticker}
        with open(self.tickers_map_file, 'w') as f:
            json.dump(res, f, indent=2)
        return res

    def get_small_cap_universe(self, min_mcap=50e6, max_mcap=500e6, max_tickers=1000) -> list:
        """
        Fetches small-cap universe ($50M-$500M market cap).
        """
        cache_file = os.path.join(self.cache_dir, 'small_cap_tickers.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)

        ticker_map = self.get_sec_ticker_map()['ticker_to_cik']
        candidates = [t for t in ticker_map.keys() if t.isalpha() and len(t) <= 5]
        
        print(f"Scanning {len(candidates)} SEC candidate tickers for small-cap market cap (${min_mcap/1e6:.0f}M-${max_mcap/1e6:.0f}M)...")
        
        small_caps = []
        def check_ticker(sym):
            try:
                t = yf.Ticker(sym)
                mc = t.fast_info.get('marketCap')
                if mc and min_mcap <= mc <= max_mcap:
                    return {'ticker': sym, 'marketCap': mc, 'cik': ticker_map[sym]}
            except Exception:
                pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(check_ticker, s) for s in candidates[:max_tickers]]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res:
                    small_caps.append(res)

        print(f"Found {len(small_caps)} small-cap tickers in scanned sample.")
        with open(cache_file, 'w') as f:
            json.dump(small_caps, f, indent=2)
        return small_caps

    def parse_form4_xml(self, xml_text: str) -> list:
        """
        Parses Form 4 XML string. Extracts qualifying open-market purchases (Code "P"),
        >= $25k value, non-10b5-1, filed by Officers or Directors.
        """
        qualifying_buys = []
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return qualifying_buys

        # 1. Check reporting owner relationship
        owner_elem = root.find('.//reportingOwner')
        if owner_elem is None:
            return qualifying_buys

        owner_name_elem = owner_elem.find('.//rptOwnerName')
        owner_cik_elem = owner_elem.find('.//rptOwnerCik')
        owner_name = owner_name_elem.text.strip() if owner_name_elem is not None and owner_name_elem.text else 'Unknown'
        owner_cik = owner_cik_elem.text.strip() if owner_cik_elem is not None and owner_cik_elem.text else owner_name

        is_dir = owner_elem.find('.//isDirector')
        is_off = owner_elem.find('.//isOfficer')
        is_director = is_dir is not None and is_dir.text in ['1', 'true', 'True']
        is_officer = is_off is not None and is_off.text in ['1', 'true', 'True']

        if not (is_director or is_officer):
            return qualifying_buys

        # 2. Check 10b5-1 Plan flag tag
        is_10b51_elem = root.find('.//isRule10b51Plan')
        if is_10b51_elem is not None and is_10b51_elem.text in ['1', 'true', 'True']:
            return qualifying_buys

        # 3. Check footnotes for 10b5-1 mention
        footnotes_text = ''
        for fn in root.findall('.//footnote'):
            if fn.text:
                footnotes_text += ' ' + fn.text
        if re.search(r'10b5-1|rule 10b5-1', footnotes_text, re.IGNORECASE):
            return qualifying_buys

        # 4. Check non-derivative transactions
        for trans in root.findall('.//nonDerivativeTransaction'):
            code_elem = trans.find('.//transactionCoding/transactionCode')
            code = code_elem.text.strip() if code_elem is not None and code_elem.text else ''
            if code != 'P':
                continue

            acq_disp_elem = trans.find('.//transactionAmounts/transactionAcquiredDisposedCode/value')
            acq_disp = acq_disp_elem.text.strip() if acq_disp_elem is not None and acq_disp_elem.text else ''
            if acq_disp != 'A':
                continue

            shares_elem = trans.find('.//transactionAmounts/transactionShares/value')
            price_elem = trans.find('.//transactionPricePerShare/value')
            t_date_elem = trans.find('.//transactionDate/value')

            t_date = t_date_elem.text.strip() if t_date_elem is not None and t_date_elem.text else None

            try:
                shares = float(shares_elem.text) if shares_elem is not None and shares_elem.text else 0.0
                price = float(price_elem.text) if price_elem is not None and price_elem.text else 0.0
                val = shares * price
            except ValueError:
                continue

            if val >= 25000.0:
                qualifying_buys.append({
                    'owner_name': owner_name,
                    'owner_cik': owner_cik,
                    'is_director': is_director,
                    'is_officer': is_officer,
                    'transaction_date': t_date,
                    'shares': shares,
                    'price': price,
                    'value': val
                })

        return qualifying_buys

    def fetch_insider_buys_for_ticker(self, cik: str, symbol: str, start_date='2023-01-01') -> list:
        """
        Fetches Form 4 filings for a ticker via SEC Submissions API.
        """
        cik_str = str(cik).zfill(10)
        url = f'https://data.sec.gov/submissions/CIK{cik_str}.json'
        
        try:
            r = requests.get(url, headers=SEC_HEADERS, timeout=10)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []

        recent = data.get('filings', {}).get('recent', {})
        forms = recent.get('form', [])
        filing_dates = recent.get('filingDate', [])
        accessions = recent.get('accessionNumber', [])
        primary_docs = recent.get('primaryDocument', [])

        buys = []
        for i, form in enumerate(forms):
            if form != '4':
                continue
            f_date = filing_dates[i]
            if f_date < start_date:
                continue

            acc = accessions[i].replace('-', '')
            doc = primary_docs[i].split('/')[-1]
            xml_url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}'

            try:
                time.sleep(0.08)  # Rate limit compliance
                r_xml = requests.get(xml_url, headers=SEC_HEADERS, timeout=8)
                if r_xml.status_code != 200 or '<ownershipDocument>' not in r_xml.text:
                    continue

                parsed_buys = self.parse_form4_xml(r_xml.text)
                for b in parsed_buys:
                    b['symbol'] = symbol
                    b['cik'] = cik
                    b['filing_date'] = f_date
                    if not b['transaction_date']:
                        b['transaction_date'] = f_date
                    buys.append(b)
            except Exception:
                pass

        return buys

    def group_into_clusters(self, buys: list, window_days=30, min_distinct_insiders=3) -> list:
        """
        Groups qualifying buys into cluster events (>= min_distinct_insiders distinct insiders
        at the same company within a rolling window_days).
        """
        if not buys:
            return []

        df = pd.DataFrame(buys)
        df['filing_date_dt'] = pd.to_datetime(df['filing_date'])
        df = df.sort_values('filing_date_dt')

        clusters = []
        for symbol, group in df.groupby('symbol'):
            group = group.sort_values('filing_date_dt')
            records = group.to_dict('records')

            # Rolling window search
            for i in range(len(records)):
                window_start = records[i]['filing_date_dt']
                window_end = window_start + timedelta(days=window_days)

                window_buys = [r for r in records if window_start <= r['filing_date_dt'] <= window_end]
                
                # Check distinct insiders
                distinct_insiders = set(r['owner_cik'] for r in window_buys)
                if len(distinct_insiders) >= min_distinct_insiders:
                    # Date of cluster trigger (filing date of the 3rd distinct insider)
                    sorted_by_filing = sorted(window_buys, key=lambda x: x['filing_date_dt'])
                    insiders_seen = set()
                    trigger_date = sorted_by_filing[-1]['filing_date']
                    for b in sorted_by_filing:
                        insiders_seen.add(b['owner_cik'])
                        if len(insiders_seen) == min_distinct_insiders:
                            trigger_date = b['filing_date']
                            break

                    cluster_id = f"{symbol}_{window_start.strftime('%Y%m%d')}_{len(distinct_insiders)}"
                    
                    # Deduplicate overlapping clusters for same symbol within 15 days
                    already_exists = False
                    for existing in clusters:
                        if existing['symbol'] == symbol:
                            dt_diff = abs((pd.to_datetime(trigger_date) - pd.to_datetime(existing['trigger_date'])).days)
                            if dt_diff <= 15:
                                already_exists = True
                                break

                    if not already_exists:
                        total_value = sum(b['value'] for b in window_buys)
                        insider_names = list(set(b['owner_name'] for b in window_buys))
                        clusters.append({
                            'cluster_id': cluster_id,
                            'symbol': symbol,
                            'cik': window_buys[0]['cik'],
                            'window_start_date': window_start.strftime('%Y-%m-%d'),
                            'trigger_date': trigger_date,
                            'distinct_insiders': len(distinct_insiders),
                            'insider_names': insider_names,
                            'total_cluster_value': total_value,
                            'buys_count': len(window_buys)
                        })

        clusters.sort(key=lambda x: x['trigger_date'])
        return clusters
