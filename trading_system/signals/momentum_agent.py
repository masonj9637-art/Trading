import pandas as pd
from signals.ranking import PortfolioRanker

class MomentumAgent:
    def __init__(self, lookback=20):
        self.lookback = lookback
        self.ranker = PortfolioRanker()
        
    def generate_signal(self, close_data: pd.DataFrame) -> pd.Series:
        """
        Generates portfolio weights based on cross-sectional momentum.
        close_data: shape (lookback, assets)
        """
        if len(close_data) < self.lookback:
            return pd.Series(0, index=close_data.columns)
            
        # Calculate momentum (rate of change over the lookback window)
        momentum = (close_data.iloc[-1] - close_data.iloc[0]) / close_data.iloc[0]
        
        # Rank and normalize to create a dollar-neutral portfolio
        alpha_df = pd.DataFrame([momentum])
        normalized_weights = self.ranker.rank_and_normalize(alpha_df).iloc[0]
        return normalized_weights
