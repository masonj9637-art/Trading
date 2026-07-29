import time
from alpaca.trading.enums import OrderSide, TimeInForce
from execution.alpaca_client import AlpacaTradingClient
from execution.order_manager import OrderManager

client = AlpacaTradingClient()
manager = OrderManager(client)

print("1. Buying 10 DOGE/USD...")
buy_req = manager.create_market_order("DOGE/USD", "BUY", 10)
if buy_req:
    # Crypto requires GTC for market orders in Alpaca
    buy_req.time_in_force = TimeInForce.GTC
    try:
        trade = client.client.submit_order(order_data=buy_req)
        print(f"Market order ID: {trade.id}")
        
        print("Waiting 5s for fill...")
        time.sleep(5)
        
        print("2. Placing OCO for DOGE/USD...")
        oco_req = manager.create_oco_order("DOGE/USD", "SELL", 10, tp_price=0.50, sl_price=0.05)
        try:
            oco_trade = client.client.submit_order(order_data=oco_req)
            print(f"OCO order ACCEPTED! ID: {oco_trade.id}")
        except Exception as e:
            print(f"OCO error: {e}")
    except Exception as e:
        print(f"Market order error: {e}")
        
    print("Cleaning up...")
    client.cancel_all_open_orders()
    client.close_all_positions()
