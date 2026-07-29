import asyncio
import pandas as pd
from data.alpaca_fetcher import AlpacaDataFetcher
from backtest.engine import BacktestEngine
import quantstats as qs
import os

async def run_backtest():
    os.makedirs("reports", exist_ok=True)
    fetcher = AlpacaDataFetcher()
    symbols = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "BRK.B", "UNH", "JNJ", "SPY",
        "JPM", "V", "PG", "HD", "CVX", "LLY", "MA", "ABBV", "PEP", "KO"
    ]
    
    # 730 days of trading + 100 days for context window = 830 days
    print("Fetching 830 days of historical data from Alpaca...")
    market_data = await fetcher.fetch_historical_data(symbols, days=830)
    
    print("Fetching 830 days of macro data from Yahoo Finance...")
    macro_data = await fetcher.fetch_macro_data(days=830)
    
    print("Initializing Backtest Engine...")
    engine = BacktestEngine(market_data, macro_data=macro_data, initial_capital=100000.0)
    
    # Inject the optimal parameters from Optuna (Sharpe 3.18)
    engine.firewall.agent_concentration_limits['deep_ofi'] = 0.3478
    engine.firewall.agent_concentration_limits['kalman'] = 0.2753
    engine.firewall.agent_concentration_limits['chronos'] = 0.4938
    engine.firewall.var_limit = 0.1437
    engine.firewall.global_max_leverage = 1.0754
    engine.volatility_guard.tp_multiplier = 4.9520
    engine.volatility_guard.sl_multiplier = 0.6105
    risk_penalty = 2.2011
    
    print("Running Backtest Engine. This may take 5-10 minutes due to the Chronos-2 AI models...")
    history_df = engine.run(risk_penalty=risk_penalty)
    
    if not history_df.empty:
        print("Backtest complete! Generating quantstats report...")
        history_df.set_index('date', inplace=True)
        returns = history_df['capital'].pct_change().dropna()
        
        sharpe = qs.stats.sharpe(returns)
        cagr = qs.stats.cagr(returns) * 100
        max_dd = qs.stats.max_drawdown(returns) * 100
        final_value = history_df['capital'].iloc[-1]
        
        print("-" * 30)
        print("--- 2 YEAR OPTIMAL RESULTS ---")
        print(f"Final Portfolio Value: ${final_value:,.2f}")
        print(f"CAGR: {cagr:.2f}%")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Max Drawdown: {max_dd:.2f}%")
        print("-" * 30)
        
        # Save HTML tearsheet
        qs.reports.html(returns, output='reports/2_year_optimal_backtest.html')
        print("Report saved to reports/2_year_optimal_backtest.html")
    else:
        print("Backtest failed or returned empty data.")

if __name__ == "__main__":
    asyncio.run(run_backtest())
