import pytest
import asyncio
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from autogluon.timeseries import TimeSeriesDataFrame
import bootstrap_model

@pytest.mark.asyncio
async def test_bootstrap_chronological_split():
    dates = pd.bdate_range(start="2025-01-01", periods=100)
    symbols = ["AAPL", "MSFT", "NVDA"]
    
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
        
        mock_chronos.train.assert_called_once()
        ts_data_arg = mock_chronos.train.call_args[0][0]
        passed_dates = pd.to_datetime(ts_data_arg.index.get_level_values("timestamp")).unique()
        
        valid_dates = dates[1:]
        unique_dates = np.sort(pd.to_datetime(valid_dates).unique())
        split_idx = int(len(unique_dates) * 0.80)
        train_dates = unique_dates[:split_idx]
        withheld_dates = unique_dates[split_idx:]
        
        assert set(passed_dates) == set(train_dates)
        assert not set(passed_dates).intersection(set(withheld_dates))
