import unittest
from unittest.mock import MagicMock
from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
from execution.order_manager import OrderManager

class TestOrderManager(unittest.TestCase):
    def test_create_market_order(self):
        mock_client = MagicMock()
        manager = OrderManager(mock_client)
        
        req = manager.create_market_order("AAPL", "BUY", 10.5)
        
        self.assertIsNotNone(req)
        self.assertEqual(req.symbol, "AAPL")
        self.assertEqual(req.qty, 10)
        self.assertEqual(req.side, OrderSide.BUY)
        self.assertEqual(req.time_in_force, TimeInForce.DAY)
        self.assertIsNone(getattr(req, "order_class", None))

    def test_create_bracket_order(self):
        mock_client = MagicMock()
        manager = OrderManager(mock_client)
        
        req = manager.create_bracket_order("SPY", "SELL", 5, tp_price=100.123, sl_price=105.456, time_in_force=TimeInForce.GTC)
        
        self.assertIsNotNone(req)
        self.assertEqual(req.symbol, "SPY")
        self.assertEqual(req.qty, 5)
        self.assertEqual(req.side, OrderSide.SELL)
        self.assertEqual(req.time_in_force, TimeInForce.GTC)
        self.assertEqual(req.order_class, OrderClass.BRACKET)
        
        self.assertIsNotNone(req.take_profit)
        self.assertEqual(req.take_profit.limit_price, 100.12)
        
        self.assertIsNotNone(req.stop_loss)
        self.assertEqual(req.stop_loss.stop_price, 105.46)

    def test_create_oco_order(self):
        mock_client = MagicMock()
        manager = OrderManager(mock_client)
        
        req = manager.create_oco_order("NVDA", "BUY", 15, tp_price=150.555, sl_price=140.444, time_in_force=TimeInForce.GTC)
        
        self.assertIsNotNone(req)
        self.assertEqual(req.symbol, "NVDA")
        self.assertEqual(req.qty, 15)
        self.assertEqual(req.side, OrderSide.BUY)
        self.assertEqual(req.time_in_force, TimeInForce.GTC)
        self.assertEqual(req.order_class, OrderClass.OCO)
        self.assertEqual(req.limit_price, 150.56)
        
        self.assertIsNotNone(getattr(req, "take_profit", None))
        self.assertEqual(req.take_profit.limit_price, 150.56)
        
        self.assertIsNotNone(req.stop_loss)
        self.assertEqual(req.stop_loss.stop_price, 140.44)

if __name__ == "__main__":
    unittest.main()
