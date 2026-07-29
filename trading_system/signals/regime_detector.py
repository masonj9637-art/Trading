import pandas as pd
import numpy as np

class RegimeDetector:
    def __init__(self, short_window=20, long_window=50, vol_window=20, vol_threshold=1.5):
        self.short_window = short_window
        self.long_window = long_window
        self.vol_window = vol_window
        self.vol_threshold = vol_threshold
        
    def detect(self, market_data: pd.DataFrame, benchmark_symbol: str = 'SPY') -> str:
        """
        Classifies the market regime using the benchmark symbol (e.g. SPY).
        market_data: MultiIndex DataFrame (symbol, feature)
        Returns: 'BULL_TREND', 'BEAR_TREND', or 'CHOP'
        """
        try:
            benchmark_close = market_data.xs('close', level=1, axis=1)[benchmark_symbol]
        except KeyError:
            # Fallback to mean of all assets if benchmark is missing
            benchmark_close = market_data.xs('close', level=1, axis=1).mean(axis=1)
            
        if len(benchmark_close) < self.long_window:
            return 'CHOP' # Not enough data, default to chop
            
        short_ma = benchmark_close.rolling(window=self.short_window).mean().iloc[-1]
        long_ma = benchmark_close.rolling(window=self.long_window).mean().iloc[-1]
        
        daily_returns = benchmark_close.pct_change().dropna()
        current_vol = daily_returns.rolling(window=self.vol_window).std().iloc[-1]
        historical_vol = daily_returns.std()
        
        # Volatility check: if current volatility is >1.5x historical, it's a choppy/high-risk regime
        if current_vol > historical_vol * self.vol_threshold:
            return 'CHOP'
            
        # Trend check
        if short_ma > long_ma:
            return 'BULL_TREND'
        elif short_ma < long_ma:
            return 'BEAR_TREND'
            
        return 'CHOP'
