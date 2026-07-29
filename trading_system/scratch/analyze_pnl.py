import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPACA_API_KEY', '')
secret_key = os.getenv('ALPACA_SECRET_KEY', '')

headers = {
    'APCA-API-KEY-ID': api_key,
    'APCA-API-SECRET-KEY': secret_key
}

today = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')

print(f"Analyzing PnL for {today}...")

res = requests.get('https://paper-api.alpaca.markets/v2/positions', headers=headers)
positions = res.json()

unrealized_pnl = 0
worst_performers = []

for p in positions:
    pnl = float(p.get('unrealized_intraday_pl', 0))
    unrealized_pnl += pnl
    worst_performers.append({
        'symbol': p['symbol'],
        'pnl': pnl,
        'change': float(p.get('change_today', 0)) * 100,
        'qty': p['qty'],
        'market_value': p['market_value']
    })

worst_performers.sort(key=lambda x: x['pnl'])

print("\n--- Top 10 Biggest Intraday Losers (Open Positions) ---")
for p in worst_performers[:10]:
    print(f"{p['symbol']:<5} | PnL: ${p['pnl']:<8.2f} | Change: {p['change']:<6.2f}% | Qty: {p['qty']}")

print("\n--- Top 5 Biggest Intraday Winners (Open Positions) ---")
for p in worst_performers[-5:]:
    print(f"{p['symbol']:<5} | PnL: ${p['pnl']:<8.2f} | Change: {p['change']:<6.2f}% | Qty: {p['qty']}")

print(f"\nTotal Unrealized Intraday PnL: ${unrealized_pnl:.2f}")

# Let's get today's closed positions
url = f"https://paper-api.alpaca.markets/v2/account/activities/FILL?date={today}"
res = requests.get(url, headers=headers)
fills = res.json()

print(f"\nTotal Fills Today: {len(fills)}")
