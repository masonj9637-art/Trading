import quantstats as qs
import pandas as pd
import os
from datetime import datetime

class AnalyticsEngine:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def generate_tear_sheet(self, history_df: pd.DataFrame, title="AI Statistical Arbitrage Strategy"):
        """
        Takes the history dataframe from BacktestEngine and generates a quantstats HTML tear sheet.
        history_df requires columns: 'date', 'capital'
        """
        if history_df.empty:
            print("History dataframe is empty. Cannot generate report.")
            return
            
        # Ensure date is datetime and set as index
        df = history_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Export comprehensive raw data to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(self.output_dir, f"backtest_history_{timestamp}.csv")
        df.to_csv(csv_file)
        print(f"Comprehensive agent history exported to: {csv_file}")
        
        # Calculate daily returns
        returns = df['capital'].pct_change().dropna()
        
        # Generate HTML report
        output_file = os.path.join(self.output_dir, "tearsheet.html")
        qs.reports.html(returns, title=title, output=output_file)
        
        print(f"Tear sheet successfully generated at: {output_file}")
        
        # Print basic terminal metrics as well
        sharpe = qs.stats.sharpe(returns)
        if isinstance(sharpe, pd.Series): sharpe = sharpe.iloc[0]
        max_dd = qs.stats.max_drawdown(returns)
        if isinstance(max_dd, pd.Series): max_dd = max_dd.iloc[0]
        cagr = qs.stats.cagr(returns)
        if isinstance(cagr, pd.Series): cagr = cagr.iloc[0]
        
        # Generate Markdown Report
        md_dir = "Backtest reports"
        if not os.path.exists(md_dir):
            os.makedirs(md_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = title.replace(" ", "_").replace("/", "-")
        md_file = os.path.join(md_dir, f"{safe_title}_{timestamp}.md")
        
        with open(md_file, "w") as f:
            f.write(f"# {title} - Backtest Report\n\n")
            f.write(f"**Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary Metrics\n")
            f.write(f"- **CAGR:** {cagr*100:.2f}%\n")
            f.write(f"- **Sharpe Ratio:** {sharpe:.2f}\n")
            f.write(f"- **Max Drawdown:** {max_dd*100:.2f}%\n")
            f.write(f"- **Final Capital:** ${df['capital'].iloc[-1]:,.2f}\n\n")
            
            # Agent Performance Breakdown
            pnl_cols = [col for col in df.columns if col.startswith('pnl_')]
            if pnl_cols:
                f.write("## Agent Performance Summary\n")
                f.write("| Agent | Cumulative PnL | Avg Trust Weight |\n")
                f.write("|---|---|---|\n")
                for col in pnl_cols:
                    agent_name = col.replace('pnl_', '')
                    cum_pnl = df[col].sum()
                    avg_weight = df[f'weight_{agent_name}'].mean() if f'weight_{agent_name}' in df.columns else 0.0
                    f.write(f"| {agent_name.capitalize()} | ${cum_pnl:,.2f} | {avg_weight*100:.1f}% |\n")
                f.write("\n")
                
        print(f"Markdown report generated at: {md_file}")
        
        print("\n--- Summary Metrics ---")
        print(f"CAGR: {cagr*100:.2f}%")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Max Drawdown: {max_dd*100:.2f}%")
