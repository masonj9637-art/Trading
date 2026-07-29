import pandas as pd

class AlphaIsolator:
    def __init__(self, alpha=0.25):
        self.alpha = alpha
        
    def isolate(self, expected_forward_returns: pd.DataFrame, smoothed_returns: pd.DataFrame) -> pd.DataFrame:
        """
        Strips out the autoregressive momentum component to calculate the adjusted predictive alpha signal:
        chi_tilde = chi_hat - alpha * r_hat
        """
        # Align dataframes in case of missing data
        expected, smoothed = expected_forward_returns.align(smoothed_returns, join='inner')
        return expected - (self.alpha * smoothed)
