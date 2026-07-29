import os
import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

try:
    with open('/home/mason/Trading/.env') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                os.environ[k] = v
except Exception:
    pass

api_key = os.getenv('ALPACA_API_KEY', '')
secret_key = os.getenv('ALPACA_SECRET_KEY', '')

client = TradingClient(api_key, secret_key, paper=True)
now = datetime.datetime.now(datetime.timezone.utc)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

req = GetOrdersRequest(
    status=QueryOrderStatus.CLOSED,
    limit=500,
    after=today_start
)
orders = client.get_orders(filter=req)

tp_hits = 0
sl_hits = 0

print("Analyzing filled orders today...")
for o in orders:
    if o.status.name == 'FILLED':
        if o.order_type.name == 'LIMIT':
            tp_hits += 1
            print(f"[TP HIT] {o.symbol} {o.side.name} {o.qty} @ {o.filled_avg_price}")
        elif o.order_type.name in ('STOP', 'STOP_LIMIT'):
            sl_hits += 1
            print(f"[SL HIT] {o.symbol} {o.side.name} {o.qty} @ {o.filled_avg_price}")

print(f"\nTotal Take Profits Hit Today: {tp_hits}")
print(f"Total Stop Losses Hit Today: {sl_hits}")
