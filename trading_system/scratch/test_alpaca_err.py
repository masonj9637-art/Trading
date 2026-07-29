import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import json

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

print("Trying BUY...")
try:
    req = MarketOrderRequest(symbol="PG", qty=47, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
    client.submit_order(req)
except Exception as e:
    print(f"BUY ERROR: {e}")

print("Trying SELL...")
try:
    req = MarketOrderRequest(symbol="PG", qty=47, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
    client.submit_order(req)
except Exception as e:
    print(f"SELL ERROR: {e}")

