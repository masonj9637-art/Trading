import sys
import os
sys.path.append('.')
try:
    from execution.alpaca_client import AlpacaTradingClient
    client = AlpacaTradingClient()
    positions = client.get_open_positions()
    orders = client.client.get_orders()
    print("--- POSITIONS ---")
    for p in positions:
        print(f"{p.symbol}: {p.qty} shares (Side: {p.side.name}) - PnL: ${p.unrealized_pl}")
    print("\n--- ORDERS ---")
    for o in orders:
        print(f"{o.symbol}: {o.side.name} {o.qty} shares - Type: {o.type.name} - Status: {o.status.name}")
except Exception as e:
    print(f"Error: {e}")
