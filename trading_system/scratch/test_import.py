import asyncio
from main import TradingSystem

async def run_test():
    ts = TradingSystem()
    # Mock order manager
    class DummyOrderManager:
        def create_market_order(self, symbol, action, quantity):
            print(f"create_market_order({symbol}, {action}, {quantity})")
            return "dummy_req"
        async def route_order_async(self, order):
            print("route_order_async()")
            return None

    ts.order_manager = DummyOrderManager()
    
    # Test TSLA
    print("Testing TSLA...")
    await ts._execute_position_change('TSLA', -10.2754, 8.0, label="Non-OFI/GTC")
    
    print("Testing PG...")
    await ts._execute_position_change('PG', 47.4640, -43.0, label="Non-OFI/GTC")

asyncio.run(run_test())

