from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import Dict, List, Any
from autogluon.timeseries import TimeSeriesDataFrame
from .model import ChronosInference

app = FastAPI(title="Chronos-2 Inference Service")
inference_engine = ChronosInference()

class ForecastRequest(BaseModel):
    # Expecting a serialized list of dicts: [{'item_id': 'AAPL', 'timestamp': '2023-01-01', 'target': 0.05}]
    data: List[Dict[str, Any]]

@app.on_event("startup")
def startup_event():
    # Pre-load model weights into VRAM
    inference_engine.load()

@app.post("/v1/timeseries/forecast")
def forecast(request: ForecastRequest):
    try:
        df = pd.DataFrame(request.data)
        
        # Ensure timestamp is datetime and timezone-naive
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        
        # Convert to TimeSeriesDataFrame
        ts_data = TimeSeriesDataFrame.from_data_frame(
            df,
            id_column="item_id",
            timestamp_column="timestamp"
        )
        
        # Predict
        predictions = inference_engine.predict(ts_data)
        
        # Reset index to return JSON structure
        pred_df = predictions.reset_index()
        pred_df['timestamp'] = pred_df['timestamp'].dt.strftime('%Y-%m-%d')
        
        result = pred_df.to_dict(orient="records")
        
        import gc
        del df, ts_data, predictions, pred_df
        gc.collect()
        
        return {"status": "success", "predictions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
