import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_data(universe_path, market_data_path):
    with open(universe_path, 'r') as f:
        universe = json.load(f)

    market_df = pd.read_csv(market_data_path)
    market_df['date'] = pd.to_datetime(market_df['date'])
    market_df.sort_values(['ticker', 'date'], inplace=True)
    market_df.reset_index(drop=True, inplace=True)

    return universe, market_df

def get_trading_days(market_df):
    trading_days = sorted(market_df['date'].unique())
    return trading_days

def find_effective_trading_date(filing_date_str, acceptance_time_str, trading_days_set, trading_days_list):
    fdate = pd.to_datetime(filing_date_str)
    
    is_amc = False
    if acceptance_time_str:
        try:
            acc_dt = pd.to_datetime(acceptance_time_str)
            if acc_dt.hour >= 20 or (acc_dt.hour == 16 and acc_dt.tz is None):
                is_amc = True
        except Exception:
            pass

    if is_amc:
        fdate = fdate + timedelta(days=1)

    while fdate not in trading_days_set and fdate <= trading_days_list[-1]:
        fdate = fdate + timedelta(days=1)

    return fdate

def compute_events_dataset(universe, market_df, cost_bps=10.0):
    trading_days_list = get_trading_days(market_df)
    trading_days_set = set(trading_days_list)
    trading_day_map = {d: i for i, d in enumerate(trading_days_list)}

    price_dict = market_df.set_index(['ticker', 'date'])['close'].to_dict()
    volume_dict = market_df.set_index(['ticker', 'date'])['volume'].to_dict()

    events = []
    
    for company in universe:
        ticker = company['ticker']
        for f in company['filings']:
            fdate_str = f['filing_date']
            acc_time_str = f.get('acceptance_time', '')
            
            t0 = find_effective_trading_date(fdate_str, acc_time_str, trading_days_set, trading_days_list)
            
            if t0 not in trading_day_map:
                continue

            t0_idx = trading_day_map[t0]
            if t0_idx < 1:
                continue

            t_minus1 = trading_days_list[t0_idx - 1]
            p_minus1 = price_dict.get((ticker, t_minus1))
            p0 = price_dict.get((ticker, t0))

            if p_minus1 is None or p0 is None or p_minus1 <= 0 or p0 <= 0:
                continue

            # 1-Day Price Reaction (Surprise Proxy)
            r_1d = (p0 - p_minus1) / p_minus1

            # Sanity cap on extreme data anomalies / stock splits unadjusted in raw feed
            if abs(r_1d) > 2.0: # > 200% single day move is split anomaly
                continue

            r_20d = None
            r_60d = None

            if t0_idx + 20 < len(trading_days_list):
                t_20 = trading_days_list[t0_idx + 20]
                p_20 = price_dict.get((ticker, t_20))
                if p_20 is not None and p_20 > 0:
                    r_20d = ((p_20 - p0) / p0) - (cost_bps / 10000.0)

            if t0_idx + 60 < len(trading_days_list):
                t_60 = trading_days_list[t0_idx + 60]
                p_60 = price_dict.get((ticker, t_60))
                if p_60 is not None and p_60 > 0:
                    r_60d = ((p_60 - p0) / p0) - (cost_bps / 10000.0)

            events.append({
                'ticker': ticker,
                'filing_date': fdate_str,
                'effective_t0': t0,
                't0_idx': t0_idx,
                'p_minus1': p_minus1,
                'p0': p0,
                'r_1d': r_1d,
                'r_20d_net': r_20d,
                'r_60d_net': r_60d
            })

    events_df = pd.DataFrame(events)
    events_df.sort_values('effective_t0', inplace=True)
    events_df.reset_index(drop=True, inplace=True)
    return events_df, trading_days_list, price_dict

def generate_random_baseline(universe, market_df, earnings_events_df, trading_days_list, price_dict, cost_bps=10.0, num_samples_per_ticker=10):
    np.random.seed(42)
    
    earnings_dates = set()
    for _, row in earnings_events_df.iterrows():
        t0_idx = row['t0_idx']
        for delta in range(-15, 16):
            if 0 <= t0_idx + delta < len(trading_days_list):
                earnings_dates.add((row['ticker'], trading_days_list[t0_idx + delta]))

    random_events = []
    trading_day_map = {d: i for i, d in enumerate(trading_days_list)}

    for company in universe:
        ticker = company['ticker']
        ticker_bars = market_df[market_df['ticker'] == ticker]
        valid_dates = ticker_bars['date'].tolist()

        candidate_dates = [d for d in valid_dates if (ticker, d) not in earnings_dates]
        if len(candidate_dates) < 15:
            continue

        selected_dates = np.random.choice(candidate_dates, size=min(num_samples_per_ticker, len(candidate_dates)), replace=False)

        for t0 in selected_dates:
            t0 = pd.to_datetime(t0)
            if t0 not in trading_day_map:
                continue
            t0_idx = trading_day_map[t0]
            if t0_idx < 1:
                continue

            t_minus1 = trading_days_list[t0_idx - 1]
            p_minus1 = price_dict.get((ticker, t_minus1))
            p0 = price_dict.get((ticker, t0))

            if p_minus1 is None or p0 is None or p_minus1 <= 0 or p0 <= 0:
                continue

            r_1d = (p0 - p_minus1) / p_minus1

            if abs(r_1d) > 2.0:
                continue

            r_20d = None
            r_60d = None

            if t0_idx + 20 < len(trading_days_list):
                t_20 = trading_days_list[t0_idx + 20]
                p_20 = price_dict.get((ticker, t_20))
                if p_20 is not None and p_20 > 0:
                    r_20d = ((p_20 - p0) / p0) - (cost_bps / 10000.0)

            if t0_idx + 60 < len(trading_days_list):
                t_60 = trading_days_list[t0_idx + 60]
                p_60 = price_dict.get((ticker, t_60))
                if p_60 is not None and p_60 > 0:
                    r_60d = ((p_60 - p0) / p0) - (cost_bps / 10000.0)

            random_events.append({
                'ticker': ticker,
                'effective_t0': t0,
                't0_idx': t0_idx,
                'r_1d': r_1d,
                'r_20d_net': r_20d,
                'r_60d_net': r_60d
            })

    random_df = pd.DataFrame(random_events)
    random_df.sort_values('effective_t0', inplace=True)
    random_df.reset_index(drop=True, inplace=True)
    return random_df

def run_pead_backtest(universe_path, market_data_path, cost_bps=10.0, is_ratio=0.70):
    print(f"\n=======================================================")
    print(f"   SMALL-CAP PEAD STRATEGY BACKTEST (SEC 8-K Item 2.02)   ")
    print(f"=======================================================\n")
    
    universe, market_df = load_data(universe_path, market_data_path)
    print(f"Liquid Universe Tickers (>= 10k ADV): {len(universe)}")
    print(f"Total Market Bar Records: {len(market_df)}")

    # 1. Compute Earnings Events
    events_df, trading_days_list, price_dict = compute_events_dataset(universe, market_df, cost_bps=cost_bps)
    print(f"Total Valid Item 2.02 Earnings Events: {len(events_df)}")

    # 2. Chronological Walk-Forward Split (70% IS / 30% OOS)
    events_df.sort_values('effective_t0', inplace=True)
    events_df.reset_index(drop=True, inplace=True)

    n_events = len(events_df)
    n_is = int(n_events * is_ratio)
    
    is_df = events_df.iloc[:n_is].copy()
    oos_df = events_df.iloc[n_is:].copy()

    is_min_date = is_df['effective_t0'].min().strftime('%Y-%m-%d')
    is_max_date = is_df['effective_t0'].max().strftime('%Y-%m-%d')
    oos_min_date = oos_df['effective_t0'].min().strftime('%Y-%m-%d')
    oos_max_date = oos_df['effective_t0'].max().strftime('%Y-%m-%d')

    print(f"\n--- Walk-Forward Chronological Partition ---")
    print(f"In-Sample (IS - 70%):  {len(is_df)} events ({is_min_date} to {is_max_date})")
    print(f"Out-of-Sample (OOS - 30%): {len(oos_df)} events ({oos_min_date} to {oos_max_date})")

    # 3. Derive Quintile Thresholds strictly from In-Sample 1-day price reactions
    is_q80_threshold = is_df['r_1d'].quantile(0.80)
    is_q20_threshold = is_df['r_1d'].quantile(0.20)

    print(f"\n--- In-Sample Quintile Thresholds (1-Day Surprise Proxy R_1d) ---")
    print(f"Top 20% (Quintile 5) Threshold (Strong Positive Surprise): >= +{is_q80_threshold*100:.2f}%")
    print(f"Bottom 20% (Quintile 1) Threshold (Strong Negative Surprise): <= {is_q20_threshold*100:.2f}%")

    # 4. Filter Top Quintile (Q5) and Bottom Quintile (Q1) in IS and OOS
    is_q5 = is_df[is_df['r_1d'] >= is_q80_threshold].copy()
    oos_q5 = oos_df[oos_df['r_1d'] >= is_q80_threshold].copy()

    is_q1 = is_df[is_df['r_1d'] <= is_q20_threshold].copy()
    oos_q1 = oos_df[oos_df['r_1d'] <= is_q20_threshold].copy()

    # 5. Generate Random Baseline across Universe
    random_df = generate_random_baseline(universe, market_df, events_df, trading_days_list, price_dict, cost_bps=cost_bps)
    
    cutoff_date = oos_df['effective_t0'].min()
    is_rand = random_df[random_df['effective_t0'] < cutoff_date].copy()
    oos_rand = random_df[random_df['effective_t0'] >= cutoff_date].copy()

    # Helper function for summary metrics
    def summarize_returns(df, col, label):
        valid = df[col].dropna()
        if len(valid) == 0:
            return {'label': label, 'count': 0, 'mean': 0.0, 'median': 0.0, 'win_rate': 0.0, 'std': 0.0}
        return {
            'label': label,
            'count': len(valid),
            'mean': valid.mean() * 100,
            'median': valid.median() * 100,
            'win_rate': (valid > 0).mean() * 100,
            'std': valid.std() * 100
        }

    # Summary table results
    results = {
        # Q5 Top Quintile
        'IS_Q5_20d': summarize_returns(is_q5, 'r_20d_net', 'IS Top-Quintile (Q5) 20d Drift'),
        'IS_Q5_60d': summarize_returns(is_q5, 'r_60d_net', 'IS Top-Quintile (Q5) 60d Drift'),
        'OOS_Q5_20d': summarize_returns(oos_q5, 'r_20d_net', 'OOS Top-Quintile (Q5) 20d Drift'),
        'OOS_Q5_60d': summarize_returns(oos_q5, 'r_60d_net', 'OOS Top-Quintile (Q5) 60d Drift'),

        # Q1 Bottom Quintile
        'IS_Q1_20d': summarize_returns(is_q1, 'r_20d_net', 'IS Bottom-Quintile (Q1) 20d Drift'),
        'IS_Q1_60d': summarize_returns(is_q1, 'r_60d_net', 'IS Bottom-Quintile (Q1) 60d Drift'),
        'OOS_Q1_20d': summarize_returns(oos_q1, 'r_20d_net', 'OOS Bottom-Quintile (Q1) 20d Drift'),
        'OOS_Q1_60d': summarize_returns(oos_q1, 'r_60d_net', 'OOS Bottom-Quintile (Q1) 60d Drift'),

        # Random Baseline (Unconditional All Dates)
        'IS_Rand_20d': summarize_returns(is_rand, 'r_20d_net', 'IS Random Baseline (All) 20d'),
        'IS_Rand_60d': summarize_returns(is_rand, 'r_60d_net', 'IS Random Baseline (All) 60d'),
        'OOS_Rand_20d': summarize_returns(oos_rand, 'r_20d_net', 'OOS Random Baseline (All) 20d'),
        'OOS_Rand_60d': summarize_returns(oos_rand, 'r_60d_net', 'OOS Random Baseline (All) 60d'),
    }

    print(f"\n=========================================================================================")
    print(f"               PEAD BACKTEST RESULTS: IN-SAMPLE vs OUT-OF-SAMPLE vs BASELINE              ")
    print(f"=========================================================================================")
    print(f"{'Group / Strategy Horizon':<38} | {'N':<5} | {'Mean (%)':<9} | {'Median (%)':<10} | {'Win Rate':<8} | {'Std Dev':<8}")
    print("-" * 95)
    
    order = [
        'IS_Q5_20d', 'OOS_Q5_20d', 'IS_Rand_20d', 'OOS_Rand_20d',
        'IS_Q5_60d', 'OOS_Q5_60d', 'IS_Rand_60d', 'OOS_Rand_60d',
        'IS_Q1_20d', 'OOS_Q1_20d', 'IS_Q1_60d', 'OOS_Q1_60d'
    ]
    for key in order:
        r = results[key]
        print(f"{r['label']:<38} | {r['count']:<5} | {r['mean']:>+8.2f}% | {r['median']:>+9.2f}% | {r['win_rate']:>7.1f}% | {r['std']:>7.2f}%")

    print("=========================================================================================\n")

    # Save detailed summary json
    summary_path = '/home/mason/Trading/scratch/pead_results_summary.json'
    with open(summary_path, 'w') as f:
        json.dump({
            'is_date_range': [is_min_date, is_max_date],
            'oos_date_range': [oos_min_date, oos_max_date],
            'liquid_universe_count': len(universe),
            'total_events_count': len(events_df),
            'is_q80_threshold': is_q80_threshold,
            'is_q20_threshold': is_q20_threshold,
            'cost_bps': cost_bps,
            'results': results
        }, f, indent=2)
    print(f"Saved results summary JSON to {summary_path}")

    return results, is_df, oos_df, is_q80_threshold

if __name__ == '__main__':
    run_pead_backtest(
        '/home/mason/Trading/scratch/pead_liquid_universe.json',
        '/home/mason/Trading/scratch/pead_market_data.csv',
        cost_bps=10.0,
        is_ratio=0.70
    )
