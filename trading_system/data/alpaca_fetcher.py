import pandas as pd
import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from datetime import datetime, timedelta
import yfinance as yf

class AlpacaDataFetcher:
    def __init__(self):
        api_key = os.getenv('ALPACA_API_KEY', '')
        secret_key = os.getenv('ALPACA_SECRET_KEY', '')
        if not api_key or not secret_key:
            print("WARNING: Alpaca API keys not found in environment. Data fetch will fail.")
        self.client = StockHistoricalDataClient(api_key, secret_key)
        
    async def fetch_live_prices(self, symbols: list) -> dict:
        """
        Fetches the latest trade prices for the given symbols.
        Returns a dictionary mapping symbol to its latest price.
        """
        from alpaca.data.requests import StockLatestTradeRequest
        req = StockLatestTradeRequest(symbol_or_symbols=symbols)
        try:
            trades = self.client.get_stock_latest_trade(req)
            return {sym: float(trade.price) for sym, trade in trades.items()}
        except Exception as e:
            print(f"Failed to fetch live trades: {e}")
            return {}

    async def fetch_historical_data(self, symbols: list, days=150, end_date=None) -> pd.DataFrame:
        """
        Fetches daily bars for the given symbols from Alpaca.
        Returns a wide-format DataFrame (index=dates, columns=assets) containing closing prices.
        """
        if end_date is None:
            end_date = datetime.today()
        start_date = end_date - timedelta(days=days)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
            feed=DataFeed.IEX
        )
        
        print(f"Fetching {days} days of historical data from Alpaca for {len(symbols)} symbols...")
        try:
            bars = self.client.get_stock_bars(request_params).df
        except Exception as e:
            print(f"Alpaca fetch failed: {e}")
            return pd.DataFrame()
            
        if bars.empty:
            print("Alpaca returned empty DataFrame.")
            return pd.DataFrame()
            
        # Reset MultiIndex (symbol, timestamp) to pivot
        bars_reset = bars.reset_index()
        
        # Normalize timestamp to just the date
        bars_reset['timestamp'] = pd.to_datetime(bars_reset['timestamp']).dt.tz_localize(None).dt.normalize()
        
        # Pivot: index=timestamp, columns=symbol, values=[open, high, low, close, volume]
        wide_df = bars_reset.pivot(index='timestamp', columns='symbol', values=['open', 'high', 'low', 'close', 'volume'])
        
        # Swap levels so columns are (symbol, feature) instead of (feature, symbol)
        wide_df = wide_df.swaplevel(axis=1).sort_index(axis=1)
        
        return wide_df

    async def fetch_macro_data(self, days=150, end_date=None) -> pd.DataFrame:
        """
        Fetches macroeconomic covariates (^VIX, ^TNX) from Yahoo Finance.
        Returns a DataFrame indexed by date with columns ['vix_close', 'tnx_yield'].
        """
        if end_date is None:
            end_date = datetime.today()
        start_date = end_date - timedelta(days=days + 50)  # Extra buffer for alignment
        
        print(f"Fetching macro data (^VIX, ^TNX) via yfinance...")
        try:
            # yf.download returns a MultiIndex column DataFrame if multiple tickers
            data = yf.download(['^VIX', '^TNX'], start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
            if data.empty:
                return pd.DataFrame()
            
            # Extract closing prices
            if isinstance(data.columns, pd.MultiIndex):
                close_prices = data['Close']
            else:
                close_prices = data
                
            macro_df = pd.DataFrame(index=close_prices.index)
            if '^VIX' in close_prices.columns:
                macro_df['vix_close'] = close_prices['^VIX']
            if '^TNX' in close_prices.columns:
                macro_df['tnx_yield'] = close_prices['^TNX']
                
            macro_df.index = pd.to_datetime(macro_df.index).normalize()
            # Drop timezone information for consistency with Alpaca
            macro_df.index = macro_df.index.tz_localize(None)
            
            # Forward fill missing days
            macro_df = macro_df.ffill()
            return macro_df
            
        except Exception as e:
            print(f"Failed to fetch macro data: {e}")
            return pd.DataFrame()

