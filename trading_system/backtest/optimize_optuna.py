import asyncio
import pandas as pd
import optuna
import os
from data.alpaca_fetcher import AlpacaDataFetcher
from backtest.engine import BacktestEngine
import quantstats as qs

# Suppress Optuna logs for cleanliness
optuna.logging.set_verbosity(optuna.logging.WARNING)

async def load_data():
    fetcher = AlpacaDataFetcher()
    symbols = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "BRK.B", "UNH", "JNJ", "SPY",
        "JPM", "V", "PG", "HD", "CVX", "LLY", "MA", "ABBV", "PEP", "KO"
    ]
    print("Fetching historical data...")
    market_data = await fetcher.fetch_historical_data(symbols, days=830)
    print("Fetching macro data...")
    macro_data = await fetcher.fetch_macro_data(days=830)
    return market_data, macro_data

def main():
    market_data, macro_data = asyncio.run(load_data())
    
    print("Initializing Backtest Engine and Precomputing Signals...")
    engine = BacktestEngine(market_data, macro_data=macro_data, initial_capital=100000.0, transaction_cost_bps=5.0)
    engine.precompute_signals()
    
    # Chronological Train / Test Split
    total_dates = len(market_data.index)
    split_idx = int(total_dates * 0.70)
    
    train_start_idx = engine.context_window
    train_end_idx = split_idx
    
    test_start_idx = split_idx
    test_end_idx = total_dates - 1
    
    print(f"\nData Split Summary:")
    print(f"  Total Trading Days: {total_dates}")
    print(f"  In-Sample (Train):  indices [{train_start_idx} : {train_end_idx}] ({train_end_idx - train_start_idx} days)")
    print(f"  Out-of-Sample (Test): indices [{test_start_idx} : {test_end_idx}] ({test_end_idx - test_start_idx} days)")

    def objective(trial):
        # Suggest parameters
        engine.firewall.agent_concentration_limits['deep_ofi'] = trial.suggest_float('deep_ofi_limit', 0.01, 0.50)
        engine.firewall.agent_concentration_limits['kalman'] = trial.suggest_float('kalman_limit', 0.01, 0.50)
        engine.firewall.agent_concentration_limits['chronos'] = trial.suggest_float('chronos_limit', 0.01, 0.50)
        engine.firewall.var_limit = trial.suggest_float('var_limit', 0.01, 0.20)
        engine.firewall.global_max_leverage = trial.suggest_float('max_leverage', 1.0, 3.0)
        
        # Guard & Hunter Parameters
        engine.volatility_guard.tp_multiplier = trial.suggest_float('tp_mult', 1.0, 5.0)
        engine.volatility_guard.sl_multiplier = trial.suggest_float('sl_mult', 0.5, 4.0)
        risk_penalty = trial.suggest_float('risk_penalty', 0.5, 5.0)
        
        # Run fast backtest ONLY on training window
        history_df = engine.fast_run(start_idx=train_start_idx, end_idx=train_end_idx, risk_penalty=risk_penalty)
        
        if history_df.empty:
            return -100.0
            
        returns = history_df.set_index('date')['capital'].pct_change().dropna()
        
        # Calculate Sharpe Ratio
        if returns.std() == 0 or len(returns) < 50:
            return -100.0
            
        sharpe = qs.stats.sharpe(returns)
        if isinstance(sharpe, pd.Series):
            sharpe = sharpe.iloc[0]
            
        # Stop early if we find an incredibly good institutional Sharpe on in-sample
        if sharpe >= 3.0:
            print(f"Institutional In-Sample Goal Reached! Sharpe = {sharpe:.4f}")
            trial.study.stop()
            
        return float(sharpe)

    print("\nStarting Optuna optimization (training window only)...")
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=5000, show_progress_bar=True)
    
    print("\nOptimization Complete!")
    print("Best In-Sample Trial Parameters:")
    for key, value in study.best_trial.params.items():
        print(f"    {key}: {value:.4f}")
        
    def evaluate_period(start_i, end_i, params):
        engine.firewall.agent_concentration_limits['deep_ofi'] = params['deep_ofi_limit']
        engine.firewall.agent_concentration_limits['kalman'] = params['kalman_limit']
        engine.firewall.agent_concentration_limits['chronos'] = params['chronos_limit']
        engine.firewall.var_limit = params['var_limit']
        engine.firewall.global_max_leverage = params['max_leverage']
        engine.volatility_guard.tp_multiplier = params['tp_mult']
        engine.volatility_guard.sl_multiplier = params['sl_mult']
        risk_penalty = params['risk_penalty']
        
        hist_df = engine.fast_run(start_idx=start_i, end_idx=end_i, risk_penalty=risk_penalty)
        if hist_df.empty:
            return 0.0, 0.0, 0.0
            
        returns = hist_df.set_index('date')['capital'].pct_change().dropna()
        if returns.std() == 0 or len(returns) < 5:
            return 0.0, 0.0, 0.0
            
        sharpe = qs.stats.sharpe(returns)
        cagr = qs.stats.cagr(returns)
        max_dd = qs.stats.max_drawdown(returns)
        
        if isinstance(sharpe, pd.Series): sharpe = sharpe.iloc[0]
        if isinstance(cagr, pd.Series): cagr = cagr.iloc[0]
        if isinstance(max_dd, pd.Series): max_dd = max_dd.iloc[0]
        
        return float(sharpe), float(cagr), float(max_dd)

    in_sharpe, in_cagr, in_dd = evaluate_period(train_start_idx, train_end_idx, study.best_trial.params)
    out_sharpe, out_cagr, out_dd = evaluate_period(test_start_idx, test_end_idx, study.best_trial.params)

    print("\n" + "="*60)
    print("BACKTEST METHODOLOGY EVALUATION RESULTS")
    print("="*60)
    print("IN-SAMPLE (TRAINING WINDOW - First 70%):")
    print(f"  Sharpe Ratio:  {in_sharpe:.4f}")
    print(f"  CAGR:          {in_cagr*100:.2f}%")
    print(f"  Max Drawdown:  {in_dd*100:.2f}%")
    print("-" * 60)
    print("OUT-OF-SAMPLE (HELD-OUT TEST WINDOW - Remaining 30%): [REAL RESULT]")
    print(f"  Sharpe Ratio:  {out_sharpe:.4f}")
    print(f"  CAGR:          {out_cagr*100:.2f}%")
    print(f"  Max Drawdown:  {out_dd*100:.2f}%")
    print("="*60)
    print("SIDE-BY-SIDE SHARPE COMPARISON:")
    print(f"  In-Sample Sharpe:     {in_sharpe:.4f}")
    print(f"  Out-of-Sample Sharpe: {out_sharpe:.4f}")
    print(f"  Overfitting Gap:      {in_sharpe - out_sharpe:.4f}")
    print("="*60)

if __name__ == "__main__":
    main()
