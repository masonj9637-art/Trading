from alpaca.trading.requests import LimitOrderRequest
from typing import Optional, Dict, Any
from pydantic import Field
class AdvancedLimitOrderRequest(LimitOrderRequest):
    advanced_instructions: Optional[Dict[str, Any]] = None

req = AdvancedLimitOrderRequest(symbol='AAPL', qty=10, side='buy', time_in_force='day', limit_price=200, advanced_instructions={'algorithm': 'VWAP'})
print(req.model_dump(exclude_none=True))
