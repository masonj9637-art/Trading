import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from backtest.engine import BacktestEngine

def test_cost_model_pnl_impact():
    """
    Run backtest/engine.py's fast_run() twice on identical data/params, once with transaction_cost_bps=0.0
    and once set to 10.0 bps. Assert the nonzero-cost run's final capital is strictly lower than the zero-cost run's.
    """
    dates = pd.bdate_range(start="2024-01-01", periods=150)
    symbols = ["AAPL", "MSFT", "SPY"]
    iterables = [symbols, ["open", "high", "low", "close", "volume"]]
    cols = pd.MultiIndex.from_product(iterables, names=["symbol", "field"])
    
    data = {}
    np.random.seed(42)
    for sym in symbols:
        price = 100.0
        prices = []
        for _ in range(len(dates)):
            price += np.random.normal(0, 1.0)
            prices.append(max(price, 10.0))
        for f in ["open", "high", "low", "close"]:
            data[(sym, f)] = prices
        data[(sym, "volume")] = [10000] * len(dates)
        
    market_data = pd.DataFrame(data, index=dates)
    macro_data = pd.DataFrame({
        "vix_close": [20.0] * len(dates),
        "tnx_yield": [4.0] * len(dates)
    }, index=dates)
    
    with patch("backtest.engine.ChronosInference"):
        engine_zero = BacktestEngine(market_data, macro_data=macro_data, initial_capital=100000.0, transaction_cost_bps=0.0)
        engine_cost = BacktestEngine(market_data, macro_data=macro_data, initial_capital=100000.0, transaction_cost_bps=10.0)
        
        # Populate identical cached signals generating trading activity
        for d in dates[100:]:
            cached = {
                'regime': 'BULL_TREND',
                'chronos_weights': pd.Series({"AAPL": 0.4, "MSFT": -0.4, "SPY": 0.0}),
                'ofi_weights': pd.Series({"AAPL": 0.0, "MSFT": 0.0, "SPY": 0.0}),
                'kalman_weights': pd.Series({"AAPL": 0.0, "MSFT": 0.0, "SPY": 0.0}),
                'predictions': None,
                'volatilities': {"AAPL": 0.02, "MSFT": 0.02, "SPY": 0.02}
            }
            engine_zero.cached_signals[d] = cached
            engine_cost.cached_signals[d] = cached
            
        hist_zero = engine_zero.fast_run(start_idx=100, end_idx=149)
        hist_cost = engine_cost.fast_run(start_idx=100, end_idx=149)
        
        cap_zero = hist_zero.iloc[-1]['capital']
        cap_cost = hist_cost.iloc[-1]['capital']
        
        assert cap_cost < cap_zero, f"Nonzero cost capital ({cap_cost}) must be strictly lower than zero cost capital ({cap_zero})"
