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

# I am long 36 shares of AAPL. I will try to BUY 10 more shares.
print("Trying BUY on AAPL (we are long 36)...")
try:
    req = MarketOrderRequest(symbol="AAPL", qty=10, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
    client.submit_order(req)
    print("BUY on AAPL SUCCESSFUL (no insufficient qty error)")
except Exception as e:
    print(f"BUY ERROR: {e}")
