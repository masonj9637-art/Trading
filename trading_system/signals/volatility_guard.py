import pandas as pd
import numpy as np
from arch import arch_model

class VolatilityGuard:
    def __init__(self, tp_multiplier=2.0, sl_multiplier=1.0):
        self.tp_multiplier = tp_multiplier
        self.sl_multiplier = sl_multiplier

    def get_conditional_volatility(self, returns_series: pd.Series) -> float:
        """
        Fits a GJR-GARCH(1,1,1) model to the returns and predicts the next day's volatility.
        This captures the asymmetric 'leverage effect' where downside shocks increase volatility more than upside.
        Returns the forecasted standard deviation (volatility).
        """
        # Ensure we have enough data (at least 50 points)
        if len(returns_series) < 50:
            return returns_series.std() if len(returns_series) > 1 else 0.02
        
        # Multiply by 100 to help optimizer convergence (standard practice for GARCH)
        rescaled_returns = returns_series.dropna() * 100.0
        
        if rescaled_returns.std() == 0:
            return 0.01
            
        try:
            # p=1 (ARCH), o=1 (asymmetric GJR term), q=1 (GARCH)
            model = arch_model(rescaled_returns, vol='GARCH', p=1, o=1, q=1, dist='Normal', rescale=False)
            res = model.fit(disp='off', show_warning=False)
            forecast = res.forecast(horizon=1)
            # Forecast variance is in scaled units, divide by 10000 to get true variance
            next_var = forecast.variance.iloc[-1, 0] / 10000.0
            return np.sqrt(next_var)
        except Exception:
            # Fallback to standard deviation if GARCH fails to converge
            return returns_series.std()

    def get_bracket_bounds(self, action: str, entry_price: float, returns_series: pd.Series) -> tuple:
        """
        Returns (take_profit, stop_loss) based on asymmetric GJR-GARCH volatility forecast.
        """
        vol = self.get_conditional_volatility(returns_series)
        
        # Protect against extreme anomalies
        vol = np.clip(vol, 0.005, 0.15)
        
        # Calculate bound prices
        if action.lower() == 'buy':
            tp_price = entry_price * (1 + (vol * self.tp_multiplier))
            sl_price = entry_price * (1 - (vol * self.sl_multiplier))
        else: # Sell short
            tp_price = entry_price * (1 - (vol * self.tp_multiplier))
            sl_price = entry_price * (1 + (vol * self.sl_multiplier))
            
        return round(tp_price, 2), round(sl_price, 2)
