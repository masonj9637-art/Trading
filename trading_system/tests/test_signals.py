import pandas as pd
from signals.ranking import PortfolioRanker

def test_ranking_leverage_constraint():
    ranker = PortfolioRanker()
    
    # 3 assets
    alpha_signals = pd.DataFrame({
        "AAPL": [0.05],
        "MSFT": [0.01],
        "NVDA": [-0.03]
    }, index=["2023-01-01"])
    
    weights = ranker.rank_and_normalize(alpha_signals)
    
    # AAPL rank 3, MSFT 2, NVDA 1.
    # N=3. N/2 = 1.5
    # AAPL w = 3 - 1.5 = 1.5
    # MSFT w = 2 - 1.5 = 0.5
    # NVDA w = 1 - 1.5 = -0.5
    # Sum abs = 1.5 + 0.5 + 0.5 = 2.5
    # Normalized AAPL = 1.5 / 2.5 = 0.6
    # MSFT = 0.5 / 2.5 = 0.2
    # NVDA = -0.5 / 2.5 = -0.2
    
    assert abs(weights.loc["2023-01-01", "AAPL"] - 0.6) < 1e-6
    assert abs(weights.iloc[0].abs().sum() - 1.0) < 1e-6
