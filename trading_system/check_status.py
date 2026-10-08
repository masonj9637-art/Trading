import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

def main():
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
    
    if not api_key or not secret_key:
        print("ERROR: Missing Alpaca API keys.")
        return

    client = TradingClient(api_key, secret_key, paper=True)
    
    positions = client.get_all_positions()
    print("=== ACTIVE POSITIONS ===")
    if not positions:
        print("No active positions.")
    else:
        for p in positions:
            print(f"{p.symbol}: {p.qty} shares @ avg {p.avg_entry_price}")
            
    req = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=100)
    orders = client.get_orders(filter=req)
    print("\n=== OPEN ORDERS ===")
    if not orders:
        print("No open orders.")
    else:
        for o in orders:
            print(f"[{o.order_type.name}] {o.side.name} {o.qty} {o.symbol} - {o.status.name}")

if __name__ == "__main__":
    main()
