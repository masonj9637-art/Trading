import pandas as pd
import numpy as np

class TemporalAligner:
    def __init__(self, frequency='B'):
        # 'B' for business days, which is standard for daily financial data
        self.frequency = frequency

    def align_and_pad(self, df: pd.DataFrame, date_column: str, value_column: str, asset_column: str) -> pd.DataFrame:
        """
        Aligns a long-format DataFrame to a continuous time index, padding missing dates with NaN.
        """
        # Pivot to get dates as index and assets as columns
        df_pivot = df.pivot(index=date_column, columns=asset_column, values=value_column)
        
        # Ensure the index is datetime
        df_pivot.index = pd.to_datetime(df_pivot.index)
        
        # Create a full date range from min to max date using business days
        full_idx = pd.bdate_range(start=df_pivot.index.min(), end=df_pivot.index.max())
        
        # Reindex to inject NaNs for missing days
        df_aligned = df_pivot.reindex(full_idx)
        
        return df_aligned
