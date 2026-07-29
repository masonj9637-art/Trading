import pytest
import os
import json
import pandas as pd
from scratch.pead_strategy_backtest import load_data, compute_events_dataset, run_pead_backtest

def test_pead_pipeline_integrity():
    universe_path = '/home/mason/Trading/scratch/pead_liquid_universe.json'
    market_data_path = '/home/mason/Trading/scratch/pead_market_data.csv'

    assert os.path.exists(universe_path), "Liquid universe file missing"
    assert os.path.exists(market_data_path), "Market data CSV missing"

    universe, market_df = load_data(universe_path, market_data_path)
    
    # 1. Verify Universe Size >= 100 liquid tickers
    assert len(universe) >= 100, f"Universe size {len(universe)} is under 100 tickers requirement"

    # 2. Verify Liquidity Floor (all tickers in liquid universe average >= 10,000 shares/day)
    adv_series = market_df.groupby('ticker')['volume'].mean()
    assert (adv_series >= 10000).all(), "Found ticker in liquid dataset violating 10,000 shares/day liquidity floor"

    # 3. Verify Non-Zero Transaction Costs (Rule 1 compliance)
    cost_bps = 10.0
    events_df, trading_days_list, price_dict = compute_events_dataset(universe, market_df, cost_bps=cost_bps)
    assert len(events_df) > 0, "No valid events generated"
    assert cost_bps > 0, "Transaction costs must not be zero"

    # 4. Verify Walk-Forward Chronological Split (Rule 2 compliance)
    results, is_df, oos_df, is_threshold = run_pead_backtest(universe_path, market_data_path, cost_bps=cost_bps, is_ratio=0.70)

    is_max_date = is_df['effective_t0'].max()
    oos_min_date = oos_df['effective_t0'].min()
    assert oos_min_date >= is_max_date, "Walk-forward chronological split leak: OOS date overlaps with IS date"

    # 5. Verify Threshold set strictly on In-Sample (Rule 2 compliance)
    expected_threshold = is_df['r_1d'].quantile(0.80)
    assert abs(is_threshold - expected_threshold) < 1e-6, "Quintile threshold leak: IS threshold does not match IS distribution"
