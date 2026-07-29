import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce

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

print("Cancelling all orders...")
client.cancel_orders()

orders = client.get_orders()
print(f"Open orders remaining: {len(orders)}")
for o in orders:
    print(o.symbol, o.order_class, o.status)
