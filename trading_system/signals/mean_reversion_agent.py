import pandas as pd
from signals.ranking import PortfolioRanker

class MeanReversionAgent:
    def __init__(self, window=20):
        self.window = window
        self.ranker = PortfolioRanker()
        
    def generate_signal(self, close_data: pd.DataFrame) -> pd.Series:
        """
        Generates portfolio weights based on statistical mean reversion.
        Assets that have fallen the furthest below their moving average are bought.
        Assets that have risen the furthest above are shorted.
        """
        if len(close_data) < self.window:
            return pd.Series(0, index=close_data.columns)
            
        ma = close_data.rolling(window=self.window).mean().iloc[-1]
        current_price = close_data.iloc[-1]
        
        # Z-score simplified: distance from MA
        # We invert the sign because we want to buy assets that are below MA (-) and short assets above MA (+)
        deviation = (ma - current_price) / current_price 
        
        # Rank and normalize to create a dollar-neutral portfolio
        alpha_df = pd.DataFrame([deviation])
        normalized_weights = self.ranker.rank_and_normalize(alpha_df).iloc[0]
        return normalized_weights
