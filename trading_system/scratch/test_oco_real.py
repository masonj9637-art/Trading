import os
import asyncio
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce

load_dotenv()
api_key = os.getenv('ALPACA_API_KEY', '')
secret_key = os.getenv('ALPACA_SECRET_KEY', '')

client = TradingClient(api_key, secret_key, paper=True)

# First get an open position to make sure we have something to exit
try:
    positions = client.get_all_positions()
    if positions:
        pos = positions[0]
        symbol = pos.symbol
        qty = abs(float(pos.qty))
        side = OrderSide.SELL if float(pos.qty) > 0 else OrderSide.BUY
        
        # Current price roughly
        current_price = float(pos.current_price)
        tp_price = current_price * 1.1 if side == OrderSide.SELL else current_price * 0.9
        sl_price = current_price * 0.9 if side == OrderSide.SELL else current_price * 1.1
        
        req = LimitOrderRequest(
            symbol=symbol,
            qty=1,
            side=side,
            time_in_force=TimeInForce.GTC,
            limit_price=round(tp_price, 2),
            order_class=OrderClass.OCO,
            take_profit=TakeProfitRequest(limit_price=round(tp_price, 2)),
            stop_loss=StopLossRequest(stop_price=round(sl_price, 2))
        )
        print("Submitting OCO...")
        res = client.submit_order(req)
        print("Success:", res.id)
    else:
        print("No open positions to test OCO.")
except Exception as e:
    print("Error:", e)
