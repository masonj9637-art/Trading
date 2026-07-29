import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

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

# Try to sell 47 shares of META (we are long 19 shares)
print("Trying SELL on META (we are long 19)...")
try:
    req = MarketOrderRequest(symbol="META", qty=47, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
    client.submit_order(req)
except Exception as e:
    print(f"SELL ERROR: {e}")

