import asyncio
import os
import pandas as pd
from data.alpaca_fetcher import AlpacaDataFetcher
from signals.temporal_alignment import TemporalAligner
from core.conditional_autoencoder import DeepOrthogonalizer
import numpy as np
from signals.smoothing import EMASmoother
from inference.model import ChronosInference
from autogluon.timeseries import TimeSeriesDataFrame

async def bootstrap():
    print("Initializing Model Bootstrapping Sequence...")
    fetcher = AlpacaDataFetcher()
    
    symbols = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "BRK.B", "UNH", "JNJ", "SPY",
        "JPM", "V", "PG", "HD", "CVX", "LLY", "MA", "ABBV", "PEP", "KO",
        "AVGO", "MRK", "TMO", "COST", "CSCO", "MCD", "WMT", "CRM", "NFLX"
    ]
    print("Fetching historical data for training (300 days)...")
    raw_data = await fetcher.fetch_historical_data(symbols, days=300) 
    
    if raw_data.empty:
        print("Failed to fetch historical data. Bootstrapping aborted.")
        return
        
    print("Fetching macro data...")
    macro_data = await fetcher.fetch_macro_data(days=300)
    if macro_data.empty:
        print("Failed to fetch macro data. Bootstrapping aborted.")
        return
        
    print("Aligning and padding data...")
    full_idx = pd.bdate_range(start=raw_data.index.min(), end=raw_data.index.max())
    market_data = raw_data.reindex(full_idx)
    
    print("Extracting closing prices...")
    close_data = market_data.xs('close', level=1, axis=1)
    returns_data = close_data.pct_change(fill_method=None).dropna()
    
    print("Applying Deep Conditional Autoencoder Factor Extraction...")
    pca = DeepOrthogonalizer(num_factors=3)
    residuals = pca.orthogonalize(returns_data)
    
    print("Applying EMA Smoothing...")
    smoother = EMASmoother(alpha=0.30)
    smoothed = smoother.smooth(residuals)
    
    print("Formatting data for AutoGluon...")
    records = []
    
    for asset in smoothed.columns:
        for date, val in smoothed[asset].items():
            if pd.notna(val) and date in macro_data.index:
                # Use SPY returns as the sector proxy. If not available, use 0.0
                spy_ret = returns_data.loc[date, 'SPY'] if 'SPY' in returns_data.columns and pd.notna(returns_data.loc[date, 'SPY']) else 0.0
                
                vix = macro_data.loc[date, 'vix_close'] if pd.notna(macro_data.loc[date, 'vix_close']) else 20.0
                tnx = macro_data.loc[date, 'tnx_yield'] if pd.notna(macro_data.loc[date, 'tnx_yield']) else 4.0
                
                records.append({
                    "item_id": asset, 
                    "timestamp": date, 
                    "target": val,
                    "vix_close": vix,
                    "tnx_yield": tnx,
                    "sector_etf": spy_ret
                })
                
    df = pd.DataFrame(records)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    
    unique_dates = np.sort(df['timestamp'].unique())
    if len(unique_dates) == 0:
        print("No valid records found for training. Bootstrapping aborted.")
        return

    # Chronological 80/20 train/withheld split to prevent model-level data leakage
    split_idx = int(len(unique_dates) * 0.80)
    train_dates = unique_dates[:split_idx]
    withheld_dates = unique_dates[split_idx:]

    train_start = pd.Timestamp(train_dates[0]).strftime('%Y-%m-%d')
    train_end = pd.Timestamp(train_dates[-1]).strftime('%Y-%m-%d')
    withheld_start = pd.Timestamp(withheld_dates[0]).strftime('%Y-%m-%d')
    withheld_end = pd.Timestamp(withheld_dates[-1]).strftime('%Y-%m-%d')

    print(f"Chronological Data Split Summary:")
    print(f"  Total historical trading days: {len(unique_dates)}")
    print(f"  Training window ({len(train_dates)} days / 80.0%): {train_start} to {train_end}")
    print(f"  Withheld window ({len(withheld_dates)} days / 20.0%): {withheld_start} to {withheld_end}")

    train_df = df[df['timestamp'].isin(train_dates)].copy()

    ts_data = TimeSeriesDataFrame.from_data_frame(
        train_df,
        id_column="item_id",
        timestamp_column="timestamp"
    )
    
    print("Initiating AutoGluon Chronos-2 LoRA Fine-Tuning...")
    inference_engine = ChronosInference(model_path="model_data")
    
    try:
        inference_engine.train(ts_data)
        print("Bootstrapping complete! Model weights saved successfully.")
    except Exception as e:
        print(f"Training failed: {e}")

if __name__ == "__main__":
    asyncio.run(bootstrap())
