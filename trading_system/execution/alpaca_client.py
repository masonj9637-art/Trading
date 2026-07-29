import os
from alpaca.trading.client import TradingClient

class AlpacaTradingClient:
    def __init__(self):
        api_key = os.getenv('ALPACA_API_KEY', '')
        secret_key = os.getenv('ALPACA_SECRET_KEY', '')
        # paper=True enforces hitting the paper-api.alpaca.markets endpoint
        self.client = TradingClient(api_key, secret_key, paper=True)
        
    def get_account_value(self) -> float:
        """
        Retrieves current account equity for sizing limits.
        """
        try:
            account = self.client.get_account()
            return float(account.equity)
        except Exception as e:
            print(f"Failed to get Alpaca account value: {e}")
            return 0.0

    def get_clock(self):
        """
        Retrieves the current market clock.
        """
        try:
            return self.client.get_clock()
        except Exception as e:
            print(f"Failed to get Alpaca clock: {e}")
            return None

    def get_open_positions(self):
        """
        Retrieves all currently open positions.
        """
        try:
            return self.client.get_all_positions()
        except Exception as e:
            print(f"Failed to get Alpaca positions: {e}")
            return []

    def cancel_all_open_orders(self):
        """
        Cancels all pending or open orders to prevent conflicting executions.
        """
        try:
            self.client.cancel_orders()
            print("Successfully cancelled all open/pending orders.")
        except Exception as e:
            print(f"Failed to cancel open orders: {e}")

    def close_all_positions(self, cancel_orders: bool = True):
        """
        Closes all open positions on Alpaca.
        """
        try:
            self.client.close_all_positions(cancel_orders=cancel_orders)
            print("Successfully closed all open positions.")
        except Exception as e:
            print(f"Failed to close all open positions: {e}")

    async def async_cancel_all_and_wait(self, max_wait_sec: int = 15):
        """
        Cancels all pending/open orders and blocks until Alpaca confirms they are fully canceled.
        """
        import asyncio
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        
        self.cancel_all_open_orders()
        print("Waiting for Alpaca backend to fully process cancellations...")
        req = GetOrdersRequest(status=QueryOrderStatus.OPEN)
        
        for _ in range(max_wait_sec):
            orders = self.client.get_orders(filter=req)
            if not orders:
                print("All orders successfully cleared from backend.")
                break
            await asyncio.sleep(1.0)
