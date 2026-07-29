import sys
from alpaca.trading.enums import OrderSide, TimeInForce
from execution.alpaca_client import AlpacaTradingClient
from execution.order_manager import OrderManager

def main():
    print("=== Sandbox API Verification ===")
    try:
        client = AlpacaTradingClient()
        manager = OrderManager(client)
    except Exception as e:
        print(f"Failed to initialize Alpaca client: {e}")
        sys.exit(1)
        
    print("\n1. Testing Market Order Routing...")
    market_order = manager.create_market_order("SPY", "BUY", 1)
    if market_order:
        try:
            trade = client.client.submit_order(order_data=market_order)
            print(f"  [SUCCESS] Market Order Accepted (ID: {trade.id})")
        except Exception as e:
            print(f"  [ERROR] Market Order Rejected: {e}")
            
    print("\n2. Testing Bracket Order Routing...")
    # AAPL is >$200, so tp > current price for a BUY, sl < current price
    bracket_order = manager.create_bracket_order("AAPL", "BUY", 1, tp_price=500.0, sl_price=100.0)
    if bracket_order:
        try:
            trade = client.client.submit_order(order_data=bracket_order)
            print(f"  [SUCCESS] Bracket Order Accepted (ID: {trade.id})")
        except Exception as e:
            print(f"  [ERROR] Bracket Order Rejected: {e}")
            
    print("\n3. Testing OCO Order Routing...")
    # Since OCO requires an existing position or is used differently, the API still validates the JSON payload structure!
    oco_order = manager.create_oco_order("SPY", "SELL", 1, tp_price=1000.0, sl_price=10.0)
    if oco_order:
        try:
            trade = client.client.submit_order(order_data=oco_order)
            print(f"  [SUCCESS] OCO Order Accepted (ID: {trade.id})")
        except Exception as e:
            print(f"  [ERROR] OCO Order Rejected: {e}")
            
    print("\nCleaning up open test orders...")
    client.cancel_all_open_orders()
    print("Sandbox test completed.")

if __name__ == "__main__":
    main()
