from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from utils.logger import logger
from utils.discord_alert import discord_alerter

class OrderManager:
    def __init__(self, trading_client):
        self.trading_client = trading_client
        
    def create_market_order(self, symbol: str, action: str, quantity: float):
        """
        Formulates a standard market order for delta-based execution.
        action: 'BUY' or 'SELL'
        """
        qty = int(quantity)
        if qty <= 0:
            return None
            
        side = OrderSide.BUY if action == 'BUY' else OrderSide.SELL
        
        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY
        )
        return req

    def create_bracket_order(self, symbol: str, action: str, quantity: float, tp_price: float, sl_price: float, time_in_force: TimeInForce = TimeInForce.GTC):
        from alpaca.trading.enums import OrderClass
        qty = int(quantity)
        if qty <= 0:
            return None
            
        side = OrderSide.BUY if action == 'BUY' else OrderSide.SELL
        
        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force,
            order_class=OrderClass.BRACKET,
            take_profit=TakeProfitRequest(limit_price=round(tp_price, 2)),
            stop_loss=StopLossRequest(stop_price=round(sl_price, 2))
        )
        return req

    def create_oco_order(self, symbol: str, action: str, quantity: float, tp_price: float, sl_price: float, time_in_force: TimeInForce = TimeInForce.GTC):
        from alpaca.trading.enums import OrderClass
        qty = int(quantity)
        if qty <= 0:
            return None
            
        side = OrderSide.BUY if action == 'BUY' else OrderSide.SELL
        
        req = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force,
            limit_price=round(tp_price, 2),
            order_class=OrderClass.OCO,
            take_profit=TakeProfitRequest(limit_price=round(tp_price, 2)),
            stop_loss=StopLossRequest(stop_price=round(sl_price, 2))
        )
        return req


    async def route_order_async(self, order_request):
        """
        Routes the bracket order to Alpaca.
        """
        if order_request is None:
            return None
            
        try:
            trade = self.trading_client.client.submit_order(order_data=order_request)
            return trade
        except Exception as e:
            logger.exception(f"Failed to route order to Alpaca: {e}")
            discord_alerter.send_alert(f"🚨 **URGENT:** Failed to route order to Alpaca!\nError: `{e}`")
            return None
