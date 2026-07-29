import os
import pandas as pd
import numpy as np
from core.conditional_autoencoder import DeepOrthogonalizer
from signals.smoothing import EMASmoother
from signals.alpha_isolation import AlphaIsolator
from signals.ranking import PortfolioRanker
from signals.regime_detector import RegimeDetector
from signals.deep_ofi_agent import DeepOFIAgent
from signals.kalman_agent import AdaptiveKalmanAgent
from core.ensemble_agent import EnsembleAgent
from governance.firewall import GovernanceEngine
from inference.model import ChronosInference
from autogluon.timeseries import TimeSeriesDataFrame
from signals.volatility_guard import VolatilityGuard

class BacktestEngine:
    def __init__(self, market_data: pd.DataFrame, macro_data: pd.DataFrame, initial_capital=100000.0, transaction_cost_bps=5.0):
        self.market_data = market_data
        self.macro_data = macro_data
        self.capital = initial_capital
        self.peak_capital = initial_capital
        self.initial_capital = initial_capital
        self.transaction_cost_bps = float(transaction_cost_bps)
        
        self.pca = DeepOrthogonalizer(num_factors=3)
        self.smoother = EMASmoother(alpha=0.30)
        self.isolator = AlphaIsolator(alpha=0.30)
        self.ranker = PortfolioRanker()
        self.firewall = GovernanceEngine(var_limit=0.05, 
                                         global_max_leverage=2.0, 
                                         global_max_drawdown=0.10,
                                         ofi_max_concentration=0.40,
                                         kalman_max_concentration=0.20,
                                         chronos_max_concentration=0.20)
        
        self.regime_detector = RegimeDetector()
        self.deep_ofi_agent = DeepOFIAgent()
        self.kalman_agent = AdaptiveKalmanAgent()
        self.volatility_guard = VolatilityGuard(tp_multiplier=2.5, sl_multiplier=1.5)
        
        self.inference_engine = ChronosInference(model_path=os.getenv("MODEL_PATH", "model_data"))
        try:
            self.inference_engine.load()
        except:
            print("WARNING: Inference engine could not load weights. Bootstrapping needed.")
        
        self.context_window = 100
        self.portfolio_history = []
        
        self.cached_signals = {}
        
    def precompute_signals(self, start_idx=None):
        if start_idx is None:
            start_idx = self.context_window
            
        dates = self.market_data.index
        symbols = self.market_data.columns.levels[0]
        
        cache_path = "logs/precomputed_signals_cache.pkl"
        if os.path.exists(cache_path):
            import pickle
            try:
                with open(cache_path, 'rb') as f:
                    self.cached_signals = pickle.load(f)
                print("Loaded precomputed signals from cache.")
                return
            except Exception as e:
                print(f"Failed to load cache: {e}")
                
        print(f"Precomputing signals for {len(dates) - start_idx - 1} days...")
        for i in range(start_idx, len(dates) - 1):
            current_date = dates[i]
            
            close_data = self.market_data.xs('close', level=1, axis=1).iloc[i - self.context_window + 1 : i + 1]
            returns_data = close_data.pct_change().dropna()
            
            window_data = self.market_data.iloc[i - self.context_window + 1 : i + 1]
            
            regime = self.regime_detector.detect(window_data)
            
            residuals = self.pca.orthogonalize(returns_data)
            smoothed = self.smoother.smooth(residuals)
            
            records = []
            for asset in smoothed.columns:
                for d, val in smoothed[asset].items():
                    if pd.notna(val):
                        naive_date = d.tz_localize(None) if d.tzinfo else d
                        spy_ret = returns_data.loc[d, 'SPY'] if 'SPY' in returns_data.columns and pd.notna(returns_data.loc[d, 'SPY']) else 0.0
                        vix = 20.0
                        tnx = 4.0
                        if not self.macro_data.empty and naive_date in self.macro_data.index:
                            vix = self.macro_data.loc[naive_date, 'vix_close'] if pd.notna(self.macro_data.loc[naive_date, 'vix_close']) else 20.0
                            tnx = self.macro_data.loc[naive_date, 'tnx_yield'] if pd.notna(self.macro_data.loc[naive_date, 'tnx_yield']) else 4.0
                        
                        records.append({
                            "item_id": asset, 
                            "timestamp": d, 
                            "target": val,
                            "vix_close": vix,
                            "tnx_yield": tnx,
                            "sector_etf": spy_ret
                        })
                        
            df_records = pd.DataFrame(records)
            df_records['timestamp'] = pd.to_datetime(df_records['timestamp']).dt.tz_localize(None)
            ts_data = TimeSeriesDataFrame.from_data_frame(df_records, id_column="item_id", timestamp_column="timestamp")
            
            predictions = None
            try:
                predictions = self.inference_engine.predict(ts_data).reset_index().set_index("item_id")
                expected_forward = predictions['0.5']
                latest_smoothed = smoothed.iloc[-1]
                alpha_signal = self.isolator.isolate(expected_forward, latest_smoothed)
                alpha_df = pd.DataFrame([alpha_signal])
                chronos_weights = self.ranker.rank_and_normalize(alpha_df).iloc[0]
            except Exception as e:
                chronos_weights = pd.Series(0, index=symbols)
                
            ofi_weights = self.deep_ofi_agent.generate_signal(window_data)
            kalman_weights = self.kalman_agent.generate_signal(window_data)
            
            volatilities = {}
            for asset in returns_data.columns:
                vol = self.volatility_guard.get_conditional_volatility(returns_data[asset])
                volatilities[asset] = np.clip(vol, 0.005, 0.15)
            
            self.cached_signals[current_date] = {
                'regime': regime,
                'chronos_weights': chronos_weights,
                'ofi_weights': ofi_weights,
                'kalman_weights': kalman_weights,
                'predictions': predictions,
                'volatilities': volatilities
            }
        
        try:
            import pickle
            os.makedirs("logs", exist_ok=True)
            with open(cache_path, 'wb') as f:
                pickle.dump(self.cached_signals, f)
            print("Saved precomputed signals to cache.")
        except Exception as e:
            print(f"Failed to save cache: {e}")
            
        print("Precomputation complete.")

    def simulate_bracket_execution(self, action, quantity, tp_price, sl_price, entry_price, next_day_data):
        high = next_day_data['high']
        low = next_day_data['low']
        close = next_day_data['close']
        
        execution_price = close 
        
        if action == 'BUY':
            if low <= sl_price:
                execution_price = sl_price
            elif high >= tp_price:
                execution_price = tp_price
            raw_pnl = (execution_price - entry_price) * quantity 
        else: # SELL
            if high >= sl_price:
                execution_price = sl_price
            elif low <= tp_price:
                execution_price = tp_price
            raw_pnl = (entry_price - execution_price) * quantity
            
        if pd.isna(raw_pnl):
            return 0.0
            
        cost_rate = self.transaction_cost_bps / 10000.0
        entry_cost = entry_price * quantity * cost_rate
        exit_cost = execution_price * quantity * cost_rate
        return raw_pnl - entry_cost - exit_cost

    def fast_run(self, start_idx=None, end_idx=None, risk_penalty=2.0):
        if start_idx is None:
            start_idx = self.context_window
        if end_idx is None:
            end_idx = len(self.market_data.index) - 1
            
        dates = self.market_data.index
        symbols = self.market_data.columns.levels[0]
        
        # Reset state for fast run
        self.capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.portfolio_history = []
        self.ensemble = EnsembleAgent(agent_names=['chronos', 'deep_ofi', 'kalman'], risk_penalty=risk_penalty)
        cost_rate = self.transaction_cost_bps / 10000.0
        
        for i in range(start_idx, end_idx):
            current_date = dates[i]
            next_date = dates[i+1]
            
            if current_date not in self.cached_signals:
                continue
                
            cached = self.cached_signals[current_date]
            regime = cached['regime']
            predictions = cached['predictions']
            
            raw_agent_weights = {
                'chronos': cached['chronos_weights'],
                'deep_ofi': cached['ofi_weights'],
                'kalman': cached['kalman_weights']
            }
            
            trust_weights = self.ensemble.sample_trust_weights(regime)
            
            for agent_name, weight_series in raw_agent_weights.items():
                raw_agent_weights[agent_name] = weight_series.reindex(symbols).fillna(0)
                
            approved_weights, _ = self.firewall.evaluate_trades(raw_agent_weights, trust_weights, predictions, self.capital, self.peak_capital)
            
            daily_pnl = 0.0
            next_day_prices = self.market_data.loc[next_date]
            current_close_prices = self.market_data.loc[current_date].xs('close', level=1)
            
            for asset, weight in approved_weights.items():
                if weight == 0:
                    continue
                    
                entry_price = current_close_prices[asset]
                if pd.isna(entry_price) or entry_price <= 0:
                    continue
                    
                target_dollar = weight * self.capital
                quantity = abs(target_dollar / entry_price)
                action = 'BUY' if weight > 0 else 'SELL'
                
                if True: # Always use brackets now
                    vol = cached['volatilities'].get(asset, 0.02)
                    if action == 'BUY':
                        tp_price = entry_price * (1 + (vol * self.volatility_guard.tp_multiplier))
                        sl_price = entry_price * (1 - (vol * self.volatility_guard.sl_multiplier))
                    else:
                        tp_price = entry_price * (1 - (vol * self.volatility_guard.tp_multiplier))
                        sl_price = entry_price * (1 + (vol * self.volatility_guard.sl_multiplier))
                        
                    asset_next_day_data = next_day_prices[asset]
                    pnl = self.simulate_bracket_execution(
                        action, quantity, tp_price, sl_price, entry_price, asset_next_day_data
                    )
                else:
                    exit_price = next_day_prices[asset]['close']
                    if action == 'BUY':
                        raw_pnl = (exit_price - entry_price) * quantity
                    else:
                        raw_pnl = (entry_price - exit_price) * quantity
                    entry_cost = entry_price * quantity * cost_rate
                    exit_cost = exit_price * quantity * cost_rate
                    pnl = raw_pnl - entry_cost - exit_cost
                        
                daily_pnl += pnl
                
            agent_performances = {}
            for agent_name, weights in raw_agent_weights.items():
                agent_pnl = 0.0
                for asset, w in weights.items():
                    if w == 0: continue
                    entry = current_close_prices[asset]
                    exit = next_day_prices[asset]['close']
                    if pd.isna(entry) or entry <= 0 or pd.isna(exit): continue
                    qty = abs((w * self.capital) / entry)
                    if w > 0:
                        raw_pnl = (exit - entry) * qty
                    else:
                        raw_pnl = (entry - exit) * qty
                    entry_cost = entry * qty * cost_rate
                    exit_cost = exit * qty * cost_rate
                    agent_pnl += (raw_pnl - entry_cost - exit_cost)
                agent_performances[agent_name] = agent_pnl
                
            self.ensemble.update_posteriors(regime, agent_performances)
                
            self.capital += daily_pnl
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
                
            record = {
                "date": next_date,
                "capital": self.capital,
                "daily_pnl": daily_pnl,
                "regime": regime
            }
            
            for agent_name, pnl in agent_performances.items():
                record[f"pnl_{agent_name}"] = pnl
                record[f"weight_{agent_name}"] = trust_weights.get(agent_name, 0.0)
                
            self.portfolio_history.append(record)
            
        return pd.DataFrame(self.portfolio_history)

    def run(self, start_idx=None, end_idx=None, risk_penalty=2.0):
        if not self.cached_signals:
            self.precompute_signals(start_idx)
        return self.fast_run(start_idx, end_idx=end_idx, risk_penalty=risk_penalty)
