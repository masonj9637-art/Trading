import pandas as pd
import numpy as np
from signals.temporal_alignment import TemporalAligner

def test_temporal_alignment():
    aligner = TemporalAligner(frequency='B')
    
    # Create missing data
    dates = pd.to_datetime(['2023-01-02', '2023-01-04']) # 01-03 is missing
    df = pd.DataFrame({
        'date': dates.tolist() * 2,
        'asset': ['AAPL', 'AAPL', 'SPY', 'SPY'],
        'price': [150.0, 155.0, 400.0, 405.0]
    })
    
    aligned = aligner.align_and_pad(df, 'date', 'price', 'asset')
    
    assert len(aligned) == 3 # 02, 03, 04
    assert pd.isna(aligned.loc['2023-01-03', 'AAPL'])
    assert aligned.loc['2023-01-04', 'SPY'] == 405.0
