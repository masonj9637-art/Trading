import os
import json
import random
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Import production Alpaca fetcher
from data.alpaca_fetcher import AlpacaDataFetcher

TRANSACTION_COST_BPS = 20  # 20 bps round trip (10 bps entry + 10 bps exit)
COST_FACTOR = TRANSACTION_COST_BPS / 10000.0  # 0.0020

class InsiderClusterBacktester:
    def __init__(self, clusters_cache_file='data/insider_clusters_cache.json'):
        self.clusters_file = clusters_cache_file
        self.alpaca_fetcher = AlpacaDataFetcher()
        self.price_data_wide = pd.DataFrame()

    def load_clusters(self) -> list:
        if not os.path.exists(self.clusters_file):
            raise FileNotFoundError(f"Clusters file {self.clusters_file} not found.")
        with open(self.clusters_file, 'r') as f:
            clusters = json.load(f)
        clusters.sort(key=lambda x: x['trigger_date'])
        return clusters

    async def prefetch_all_prices(self, symbols: list):
        """
        Fetches historical daily bars for all symbols in a single batch call from Alpaca.
        Fallback to yfinance if symbol missing from Alpaca feed.
        """
        print(f"Prefetching price data from Alpaca for {len(symbols)} symbols...")
        try:
            wide_df = await self.alpaca_fetcher.fetch_historical_data(symbols, days=1100)
            self.price_data_wide = wide_df
        except Exception as e:
            print(f"Alpaca batch fetch warning: {e}")

    def evaluate_cluster_event(self, cluster: dict) -> dict:
        symbol = cluster['symbol']
        trigger_date_str = cluster['trigger_date']
        t_date = pd.to_datetime(trigger_date_str)

        # Extract series from prefetched wide_df if available
        df_sym = pd.DataFrame()
        if not self.price_data_wide.empty and symbol in self.price_data_wide.columns.get_level_values(0):
            df_sym = self.price_data_wide[symbol].dropna(how='all')

        if df_sym.empty or 'close' not in df_sym.columns:
            # Fallback to yfinance with delay
            import yfinance as yf
            import time
            try:
                time.sleep(0.05)
                start_date = (t_date - timedelta(days=400)).strftime('%Y-%m-%d')
                end_date = (t_date + timedelta(days=250)).strftime('%Y-%m-%d')
                df_sym = yf.download(symbol, start=start_date, end=end_date, progress=False)
                if isinstance(df_sym.columns, pd.MultiIndex):
                    df_sym.columns = [col[0].lower() for col in df_sym.columns]
                else:
                    df_sym.columns = [col.lower() for col in df_sym.columns]
                df_sym.index = pd.to_datetime(df_sym.index).tz_localize(None).normalize()
            except Exception:
                return None

        if df_sym.empty or 'close' not in df_sym.columns:
            return None

        hist_df = df_sym[df_sym.index <= t_date]
        future_df = df_sym[df_sym.index >= t_date]

        if len(hist_df) < 20 or len(future_df) < 20:
            return None

        entry_price = float(future_df['close'].iloc[0])

        # 52-Week High Calculation
        lookback_252 = hist_df.tail(252)
        high_52w = float(lookback_252['high'].max()) if 'high' in lookback_252.columns else float(lookback_252['close'].max())
        dist_52w_high = (entry_price - high_52w) / high_52w if high_52w > 0 else 0.0

        # Recent Trend (50-day momentum)
        lookback_50 = hist_df.tail(50)
        sma_50 = float(lookback_50['close'].mean())
        mom_50 = (entry_price - sma_50) / sma_50 if sma_50 > 0 else 0.0
        trend_regime = 'Strength' if mom_50 > 0 else 'Weakness'

        # Forward Returns at 60 and 120 trading days
        idx_60 = min(60, len(future_df) - 1)
        idx_120 = min(120, len(future_df) - 1)

        exit_60d = float(future_df['close'].iloc[idx_60])
        exit_120d = float(future_df['close'].iloc[idx_120])

        ret_60d_gross = (exit_60d - entry_price) / entry_price
        ret_120d_gross = (exit_120d - entry_price) / entry_price

        ret_60d_net = ret_60d_gross - COST_FACTOR
        ret_120d_net = ret_120d_gross - COST_FACTOR

        return {
            'cluster_id': cluster['cluster_id'],
            'symbol': symbol,
            'trigger_date': trigger_date_str,
            'entry_price': entry_price,
            'dist_52w_high': dist_52w_high,
            'mom_50d': mom_50,
            'trend_regime': trend_regime,
            'ret_60d_gross': ret_60d_gross,
            'ret_60d_net': ret_60d_net,
            'ret_120d_gross': ret_120d_gross,
            'ret_120d_net': ret_120d_net
        }

    def generate_random_baseline(self, valid_events: list, seed=42) -> list:
        random.seed(seed)
        baseline_results = []
        start_dt = pd.to_datetime('2023-01-01')
        end_dt = pd.to_datetime('2025-06-01')

        for event in valid_events:
            sym = event['symbol']
            rand_days = random.randint(0, (end_dt - start_dt).days)
            rand_date_str = (start_dt + timedelta(days=rand_days)).strftime('%Y-%m-%d')
            fake_cluster = {
                'cluster_id': f"RAND_{sym}_{rand_date_str}",
                'symbol': sym,
                'trigger_date': rand_date_str
            }
            res = self.evaluate_cluster_event(fake_cluster)
            if res:
                baseline_results.append(res)
        return baseline_results

    def run_walk_forward_backtest(self, is_ratio=0.70) -> dict:
        clusters = self.load_clusters()
        symbols = list(set(c['symbol'] for c in clusters))
        
        # Batch prefetch from Alpaca
        asyncio.run(self.prefetch_all_prices(symbols))

        evaluated_events = []
        for c in clusters:
            res = self.evaluate_cluster_event(c)
            if res:
                evaluated_events.append(res)

        print(f"Evaluated {len(evaluated_events)} cluster events with price history.")
        evaluated_events.sort(key=lambda x: x['trigger_date'])

        split_idx = int(len(evaluated_events) * is_ratio)
        is_events = evaluated_events[:split_idx]
        oos_events = evaluated_events[split_idx:]

        is_baseline = self.generate_random_baseline(is_events, seed=42)
        oos_baseline = self.generate_random_baseline(oos_events, seed=100)

        def calc_stats(events):
            if not events:
                return {}
            df = pd.DataFrame(events)
            ret60_net = df['ret_60d_net'] * 100.0
            ret120_net = df['ret_120d_net'] * 100.0
            return {
                'count': len(df),
                'mean_60d_net_%': float(ret60_net.mean()),
                'median_60d_net_%': float(ret60_net.median()),
                'win_rate_60d_%': float((ret60_net > 0).mean() * 100.0),
                'sharpe_60d': float(ret60_net.mean() / ret60_net.std() * np.sqrt(252/60)) if ret60_net.std() > 0 else 0.0,
                'mean_120d_net_%': float(ret120_net.mean()),
                'median_120d_net_%': float(ret120_net.median()),
                'win_rate_120d_%': float((ret120_net > 0).mean() * 100.0),
                'sharpe_120d': float(ret120_net.mean() / ret120_net.std() * np.sqrt(252/120)) if ret120_net.std() > 0 else 0.0,
            }

        def calc_regime_breakdown(events):
            if not events:
                return {}
            df = pd.DataFrame(events)
            st = df[df['trend_regime'] == 'Strength']
            wk = df[df['trend_regime'] == 'Weakness']
            return {
                'strength_count': len(st),
                'strength_mean_60d_%': float((st['ret_60d_net'] * 100).mean()) if not st.empty else 0.0,
                'strength_mean_120d_%': float((st['ret_120d_net'] * 100).mean()) if not st.empty else 0.0,
                'weakness_count': len(wk),
                'weakness_mean_60d_%': float((wk['ret_60d_net'] * 100).mean()) if not wk.empty else 0.0,
                'weakness_mean_120d_%': float((wk['ret_120d_net'] * 100).mean()) if not wk.empty else 0.0,
            }

        return {
            'total_evaluated_clusters': len(evaluated_events),
            'transaction_cost_bps': TRANSACTION_COST_BPS,
            'is_count': len(is_events),
            'oos_count': len(oos_events),
            'is_stats': calc_stats(is_events),
            'is_baseline_stats': calc_stats(is_baseline),
            'oos_stats': calc_stats(oos_events),
            'oos_baseline_stats': calc_stats(oos_baseline),
            'is_regime': calc_regime_breakdown(is_events),
            'oos_regime': calc_regime_breakdown(oos_events),
            'raw_is_events': is_events,
            'raw_oos_events': oos_events
        }

if __name__ == '__main__':
    backtester = InsiderClusterBacktester()
    results = backtester.run_walk_forward_backtest()
    print("\n=== WALK-FORWARD BACKTEST RESULTS ===")
    print(json.dumps({k: v for k, v in results.items() if not k.startswith('raw_')}, indent=2))
