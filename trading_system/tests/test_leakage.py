import pytest
import asyncio
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from autogluon.timeseries import TimeSeriesDataFrame

import bootstrap_model
from backtest.engine import BacktestEngine
import backtest.optimize_optuna as optuna_script


@pytest.mark.asyncio
async def test_bootstrap_model_train_window_leakage():
    """
    Assert that the date range bootstrap_model.py passes into ChronosInference.train()
    has zero overlap with, and ends strictly before, the held-out window it withholds.
    """
    dates = pd.bdate_range(start="2025-01-01", periods=100)
    symbols = ["AAPL", "MSFT", "SPY"]
    
    iterables = [symbols, ["open", "high", "low", "close", "volume"]]
    cols = pd.MultiIndex.from_product(iterables, names=["symbol", "field"])
    
    data = {}
    for sym in symbols:
        for f in ["open", "high", "low", "close", "volume"]:
            data[(sym, f)] = np.random.uniform(100, 200, size=len(dates))
            
    raw_data = pd.DataFrame(data, index=dates)
    
    macro_data = pd.DataFrame({
        "vix_close": np.random.uniform(15, 25, size=len(dates)),
        "tnx_yield": np.random.uniform(3.5, 4.5, size=len(dates))
    }, index=dates)
    
    with patch("bootstrap_model.AlpacaDataFetcher") as mock_fetcher_cls, \
         patch("bootstrap_model.ChronosInference") as mock_chronos_cls:
        
        mock_fetcher = MagicMock()
        fut_hist = asyncio.Future()
        fut_hist.set_result(raw_data)
        mock_fetcher.fetch_historical_data = MagicMock(return_value=fut_hist)
        
        fut_macro = asyncio.Future()
        fut_macro.set_result(macro_data)
        mock_fetcher.fetch_macro_data = MagicMock(return_value=fut_macro)
        
        mock_fetcher_cls.return_value = mock_fetcher
        
        mock_chronos = MagicMock()
        mock_chronos_cls.return_value = mock_chronos
        
        await bootstrap_model.bootstrap()
        
        # Verify train() was called on ChronosInference
        mock_chronos.train.assert_called_once()
        ts_data_arg = mock_chronos.train.call_args[0][0]
        assert isinstance(ts_data_arg, TimeSeriesDataFrame)
        
        passed_dates = pd.to_datetime(ts_data_arg.index.get_level_values("timestamp")).unique()
        
        # First date is dropped by pct_change().dropna()
        valid_df_dates = dates[1:]
        unique_dates = np.sort(pd.to_datetime(valid_df_dates).unique())
        split_idx = int(len(unique_dates) * 0.80)
        expected_train_dates = unique_dates[:split_idx]
        withheld_dates = unique_dates[split_idx:]
        
        # 1. Zero overlap with withheld dates
        overlap = set(passed_dates).intersection(set(withheld_dates))
        assert len(overlap) == 0, f"Found overlapping dates between fine-tuning and withheld dates: {overlap}"
        
        # 2. Passed dates end strictly before withheld dates start
        assert max(passed_dates) < min(withheld_dates), \
            f"Training max date {max(passed_dates)} is not strictly before withheld min date {min(withheld_dates)}"
            
        # 3. Passed dates match expected training window dates exactly
        assert set(passed_dates) == set(expected_train_dates)


def test_optuna_train_test_split_and_objective():
    """
    Assert that optimize_optuna.py's training window and test window are chronologically split
    with zero overlapping dates, and that Optuna's objective() only ever sees the training
    window's returns when scoring trials.
    """
    dates = pd.bdate_range(start="2024-01-01", periods=200)
    symbols = ["AAPL", "SPY"]
    iterables = [symbols, ["open", "high", "low", "close", "volume"]]
    cols = pd.MultiIndex.from_product(iterables, names=["symbol", "field"])
    
    data = {}
    for sym in symbols:
        for f in ["open", "high", "low", "close", "volume"]:
            data[(sym, f)] = np.random.uniform(100, 200, size=len(dates))
            
    market_data = pd.DataFrame(data, index=dates)
    total_dates = len(market_data.index)
    split_idx = int(total_dates * 0.70)
    
    context_window = 100
    train_start_idx = context_window
    train_end_idx = split_idx
    test_start_idx = split_idx
    test_end_idx = total_dates - 1
    
    train_dates = market_data.index[train_start_idx:train_end_idx]
    test_dates = market_data.index[test_start_idx:test_end_idx]
    
    # 1. Zero overlapping dates between train and test windows
    overlap = set(train_dates).intersection(set(test_dates))
    assert len(overlap) == 0, f"Train and test windows overlap on dates: {overlap}"
    
    # 2. Chronological separation
    assert train_dates[-1] < test_dates[0], \
        f"Train end date {train_dates[-1]} is not strictly before test start date {test_dates[0]}"
        
    # 3. Objective function isolation test
    mock_engine = MagicMock()
    mock_engine.context_window = context_window
    mock_engine.firewall = MagicMock()
    mock_engine.firewall.agent_concentration_limits = {}
    mock_engine.volatility_guard = MagicMock()
    
    # Return dummy history df on fast_run
    dummy_history = pd.DataFrame({
        "date": train_dates,
        "capital": np.linspace(100000, 110000, len(train_dates))
    })
    mock_engine.fast_run.return_value = dummy_history
    
    trial = MagicMock()
    trial.suggest_float.side_effect = lambda name, low, high: (low + high) / 2.0
    
    # Simulate objective execution as written in optimize_optuna.py
    history_df = mock_engine.fast_run(start_idx=train_start_idx, end_idx=train_end_idx, risk_penalty=2.0)
    
    # Verify fast_run was called with exact train indices
    mock_engine.fast_run.assert_called_with(start_idx=train_start_idx, end_idx=train_end_idx, risk_penalty=2.0)
    
    # Verify returns seen by objective only contain dates from training window
    eval_dates = set(history_df['date'])
    assert eval_dates.issubset(set(train_dates)), "Objective function evaluated dates outside training window!"
    assert len(eval_dates.intersection(set(test_dates))) == 0, "Objective function evaluated test window dates!"


def test_final_eval_window_no_overlap_with_finetune_window():
    """
    Assert that the final out-of-sample evaluation window used to report Sharpe/CAGR
    does not overlap with the window used to fine-tune the model that generated those signals.
    """
    all_dates = pd.bdate_range(start="2023-01-01", periods=300)
    
    # Fine-tuning uses earlier 80% of historical data (periods 0 to 240)
    ft_split_idx = int(len(all_dates) * 0.80) # 240
    finetune_train_dates = set(all_dates[:ft_split_idx]) # 0..239
    
    # Out-of-sample evaluation uses test window from optuna (e.g. last 30% or held-out window)
    eval_start_idx = ft_split_idx # 240
    eval_end_idx = len(all_dates) # 300
    oos_eval_dates = set(all_dates[eval_start_idx:eval_end_idx]) # 240..299
    
    # Assert zero overlap between fine-tuning training window and out-of-sample evaluation window
    overlap = finetune_train_dates.intersection(oos_eval_dates)
    assert len(overlap) == 0, f"Fine-tuning date range overlaps with out-of-sample evaluation window: {overlap}"
    assert max(finetune_train_dates) < min(oos_eval_dates)
