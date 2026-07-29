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

try:
    print("Submitting OCO...")
    req = LimitOrderRequest(
        symbol='F',
        qty=1,
        side=OrderSide.SELL, 
        time_in_force=TimeInForce.GTC,
        limit_price=10.0,
        order_class=OrderClass.OCO,
        take_profit=TakeProfitRequest(limit_price=10.0),
        stop_loss=StopLossRequest(stop_price=9.0)
    )
    trade = client.submit_order(req)
    print("OCO submitted!", trade.id)
    print("Legs:", len(trade.legs) if trade.legs else 0)
    if trade.legs:
        for leg in trade.legs:
            print("Leg side:", leg.side, "type:", leg.order_type, "limit:", leg.limit_price, "stop:", leg.stop_price)
except Exception as e:
    print("Error:", e)
