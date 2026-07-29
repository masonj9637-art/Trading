import os
import asyncio
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

async def test_oco():
    # Load .env manually for api keys
    try:
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    os.environ[k] = v
    except Exception:
        pass

    api_key = os.getenv('ALPACA_API_KEY', '')
    secret_key = os.getenv('ALPACA_SECRET_KEY', '')
    
    if not api_key:
        print("No API key")
        return
        
    client = TradingClient(api_key, secret_key, paper=True)
    
    # Let's try placing an OCO order directly
    # First, buy 1 share of a cheap stock to have a position
    print("Buying 1 share of F...")
    req = MarketOrderRequest(symbol="F", qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
    try:
        client.submit_order(req)
    except Exception as e:
        print(f"Buy failed: {e}")
        return
        
    await asyncio.sleep(3) # wait for fill
    
    # Now place OCO order to close
    print("Placing OCO order...")
    try:
        # What is the correct format for OCO to close?
        # Approach 1: LimitOrderRequest with order_class=OCO, take_profit, stop_loss
        oco_req = LimitOrderRequest(
            symbol="F",
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
            limit_price=15.00,
            order_class=OrderClass.OCO,
            take_profit=TakeProfitRequest(limit_price=15.00),
            stop_loss=StopLossRequest(stop_price=5.00)
        )
        res = client.submit_order(oco_req)
        print("Approach 1 succeeded!")
    except Exception as e:
        print(f"Approach 1 failed: {e}")
        
    try:
        # Approach 2: MarketOrderRequest isn't valid for OCO, but let's try LimitOrderRequest without take_profit
        oco_req2 = LimitOrderRequest(
            symbol="F",
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
            limit_price=16.00,
            order_class=OrderClass.OCO,
            stop_loss=StopLossRequest(stop_price=4.00)
        )
        res = client.submit_order(oco_req2)
        print("Approach 2 succeeded!")
    except Exception as e:
        print(f"Approach 2 failed: {e}")
        
    client.close_all_positions(cancel_orders=True)

if __name__ == "__main__":
    asyncio.run(test_oco())
