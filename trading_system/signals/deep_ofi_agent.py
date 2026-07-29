"""
DEPRECATED / UNUSED MODULE

This agent uses a Volume-Weighted Return proxy to estimate institutional order flow imbalance.
Since real Level 2 (L2) Limit Order Book data is not currently available, this proxy-based
agent has been retired from active ensemble trading and order execution loops.

Retain for reference or future activation when a real L2 data feed is integrated.
"""

import pandas as pd
import numpy as np

class DeepOFIAgent:
    def __init__(self, window=5):
        self.window = window
        
    def generate_signal(self, market_data: pd.DataFrame) -> pd.Series:
        """
        Since real L2 Limit Order Book data isn't available, we use a
        Volume-Weighted Return proxy to estimate institutional order flow imbalance.
        """
        # Extract close and volume
        try:
            close_data = market_data.xs('close', level=1, axis=1)
            volume_data = market_data.xs('volume', level=1, axis=1)
        except (KeyError, TypeError, ValueError):
            # Fallback if only close_data is passed
            close_data = market_data
            volume_data = pd.DataFrame(1.0, index=close_data.index, columns=close_data.columns)
            
        # Calculate daily returns
        returns = close_data.pct_change()
        
        # Calculate volume-weighted returns over the window
        vw_returns = (returns * volume_data).rolling(window=self.window).mean()
        
        # Get the most recent signal
        latest_vw_returns = vw_returns.iloc[-1].fillna(0)
        
        # Cross-sectional normalization
        if len(latest_vw_returns) > 0 and latest_vw_returns.std() > 0:
            latest_vw_returns = (latest_vw_returns - latest_vw_returns.mean()) / latest_vw_returns.std()
            
        return latest_vw_returns

