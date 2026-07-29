import pandas as pd

class EMASmoother:
    def __init__(self, alpha=0.25):
        # Optimizing decay parameter between 0.2 and 0.3
        self.alpha = alpha
        
    def smooth(self, residual_returns: pd.DataFrame) -> pd.DataFrame:
        """
        Applies Exponential Moving Average to the residual returns.
        r_hat_{d+1, i} = alpha * r_hat_{d, i} + r_{d+1, i}
        """
        # ewm with adjust=False matches the recursive formula in the design
        return residual_returns.ewm(alpha=self.alpha, adjust=False).mean()
