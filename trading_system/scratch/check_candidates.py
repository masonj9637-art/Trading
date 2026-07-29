import yfinance as yf
import urllib.request
import json
import time

HEADERS = {'User-Agent': 'MasonInvestments mason@example.com'}

# List of potential robotics/industrial automation candidates
candidate_tickers = [
    'PDYN', 'SERV', 'ONDS', 'RR', 'AERW', 'AEHR', 'FARO', 'HURC',
    'COHU', 'ICHR', 'UCTT', 'INDI', 'NVTS', 'AMBA', 'LPTH', 'KITT',
    'MBOT', 'MGRM', 'DUKR', 'CLPT', 'SSII', 'MDLK', 'AMCI', 'XTIA',
    'VRAR', 'LVO', 'ISDR', 'RDTN', 'SPAI', 'KSCP', 'LGVN', 'LFWD'
]

print("Checking candidate market caps...")

qualified = []

for t in candidate_tickers:
    try:
        ticker_obj = yf.Ticker(t)
        mc = getattr(ticker_obj.fast_info, 'market_cap', None)
        if mc is not None:
            mc_m = mc / 1e6
            status = "QUALIFIED" if 50 <= mc_m <= 500 else ("TOO SMALL" if mc_m < 50 else "TOO LARGE")
            print(f"{t:6s} | Market Cap: ${mc_m:7.2f}M | {status}")
            if 50 <= mc_m <= 500:
                qualified.append((t, mc_m))
        else:
            print(f"{t:6s} | Market Cap: N/A")
    except Exception as e:
        print(f"{t:6s} | Error: {e}")

print("\nQualified Tickers ($50M - $500M):")
for t, mc in qualified:
    print(f"{t}: ${mc:.2f}M")

