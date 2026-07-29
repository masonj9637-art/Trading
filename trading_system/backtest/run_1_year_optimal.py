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
    
    from datetime import datetime
    end_date = datetime(2025, 12, 31)
    # 365 days of trading + 100 days for context window = 465 days
    print("Fetching 465 days of historical data from Alpaca...")
    market_data = await fetcher.fetch_historical_data(symbols, days=465, end_date=end_date)
    
    print("Fetching 465 days of macro data from Yahoo Finance...")
    macro_data = await fetcher.fetch_macro_data(days=465, end_date=end_date)
    
    print("Initializing Backtest Engine...")
    engine = BacktestEngine(market_data, macro_data=macro_data, initial_capital=100000.0)
    
    # Inject the optimal parameters from Optuna
    engine.firewall.agent_concentration_limits['deep_ofi'] = 0.0666
    engine.firewall.agent_concentration_limits['kalman'] = 0.0403
    engine.firewall.agent_concentration_limits['chronos'] = 0.6547
    engine.firewall.var_limit = 0.0615
    engine.firewall.global_max_leverage = 1.9456
    engine.firewall.global_max_drawdown = 0.0572
    
    print("Running Backtest Engine. This may take 5-10 minutes due to the Chronos-2 AI models...")
    history_df = engine.run()
    
    if not history_df.empty:
        print("Backtest complete! Generating quantstats report...")
        history_df.set_index('date', inplace=True)
        returns = history_df['capital'].pct_change().dropna()
        
        sharpe = qs.stats.sharpe(returns)
        cagr = qs.stats.cagr(returns) * 100
        max_dd = qs.stats.max_drawdown(returns) * 100
        final_value = history_df['capital'].iloc[-1]
        
        print("-" * 30)
        print("--- 1 YEAR OPTIMAL RESULTS ---")
        print(f"Final Portfolio Value: ${final_value:,.2f}")
        print(f"CAGR: {cagr:.2f}%")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Max Drawdown: {max_dd:.2f}%")
        print("-" * 30)
        
        # Save HTML tearsheet
        qs.reports.html(returns, output='reports/1_year_optimal_backtest.html')
        print("Report saved to reports/1_year_optimal_backtest.html")
    else:
        print("Backtest failed or returned empty data.")

if __name__ == "__main__":
    asyncio.run(run_backtest())
