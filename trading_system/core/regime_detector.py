import pandas as pd

class RegimeDetector:
    def __init__(self, window=20):
        self.window = window
        
    def detect(self, market_returns: pd.DataFrame, proxy_asset='SPY') -> str:
        """
        Classifies market structure into distinct regimes.
        market_returns: df where index=dates, columns=assets
        """
        if proxy_asset not in market_returns.columns or len(market_returns) < self.window:
            return "DEFAULT"
            
        # Extract the proxy for the broad market
        returns = market_returns[proxy_asset]
        volatility = returns.rolling(window=self.window).std().iloc[-1]
        
        # Simple trend proxy (cumulative return over window)
        trend = returns.rolling(window=self.window).sum().iloc[-1]
        
        # Thresholds could be calibrated historically, using static for MVP
        vol_threshold = 0.015
        
        if trend > 0 and volatility < vol_threshold:
            return "BULL_TREND"
        elif trend > 0 and volatility >= vol_threshold:
            return "BULL_VOLATILE"
        elif trend < 0 and volatility >= vol_threshold:
            return "BEAR_HIGH_VOL"
        else:
            return "CHOP"
