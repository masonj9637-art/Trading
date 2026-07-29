import os
import re
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv('/home/mason/Trading/.env')

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
client = StockHistoricalDataClient(api_key, secret_key)

# Read small_cap_robotics_sec_filings.md
file_path = '/home/mason/Trading/small_cap_robotics_sec_filings.md'
with open(file_path, 'r') as f:
    lines = f.readlines()

filings = []
for line in lines:
    if line.startswith('|') and not 'Ticker' in line and not '|---|' in line:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 5:
            ticker = parts[0]
            company = parts[1]
            filing_type = parts[3]
            filing_date_str = parts[4]
            filings.append({
                'ticker': ticker,
                'company': company,
                'filing_type': filing_type,
                'filing_date': filing_date_str
            })

print(f"Total filings parsed: {len(filings)}")

# Fetch historical data for all unique tickers from 2026-03-01 to 2026-07-24
tickers = list(set([f['ticker'] for f in filings]))
print(f"Unique tickers: {tickers}")

req = StockBarsRequest(
    symbol_or_symbols=tickers,
    timeframe=TimeFrame.Day,
    start=datetime(2026, 3, 1),
    end=datetime(2026, 7, 24),
    feed=DataFeed.IEX
)

bars = client.get_stock_bars(req).df
bars = bars.reset_index()
bars['date'] = pd.to_datetime(bars['timestamp']).dt.tz_localize(None).dt.normalize()

print(f"Fetched {len(bars)} daily bars in total.")
print("Sample bars per ticker:")
for t in tickers:
    t_bars = bars[bars['symbol'] == t]
    print(f"  {t}: {len(t_bars)} bars, min date {t_bars['date'].min()}, max date {t_bars['date'].max()}")
