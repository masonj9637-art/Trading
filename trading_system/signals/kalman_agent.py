import pandas as pd
import numpy as np

class AdaptiveKalmanAgent:
    def __init__(self, process_noise=1e-4, measurement_noise=1e-2):
        self.q = process_noise
        self.r = measurement_noise
        
    def generate_signal(self, market_data: pd.DataFrame) -> pd.Series:
        """
        Calculates zero-lag momentum using an Adaptive Kalman Filter state-space model.
        The filter dynamically adjusts to measurement noise, holding positions during volatility 
        and tracking trends aggressively during smooth regimes.
        """
        close_data = market_data.xs('close', level=1, axis=1)
        returns = close_data.pct_change().dropna()
        
        signals = {}
        for symbol in returns.columns:
            asset_returns = returns[symbol].values
            
            # Initial state estimates
            x_hat = 0.0  # Estimated true structural drift (momentum)
            p = 1.0      # Error covariance (uncertainty)
            
            for z in asset_returns:
                if np.isnan(z): continue
                # 1. Prediction Step
                x_hat_minus = x_hat
                p_minus = p + self.q
                
                # 2. Update Step (Dynamic Kalman Gain)
                k = p_minus / (p_minus + self.r)
                x_hat = x_hat_minus + k * (z - x_hat_minus)
                p = (1 - k) * p_minus
                
            # Normalize confidence score by dividing estimated drift by mathematical standard error
            confidence = x_hat / np.sqrt(p) if p > 0 else 0
            signals[symbol] = confidence
            
        # Cross-sectional dollar-neutral normalization
        signal_series = pd.Series(signals)
        if len(signal_series) > 0 and signal_series.std() > 0:
            signal_series = (signal_series - signal_series.mean()) / signal_series.std()
            
        return signal_series
