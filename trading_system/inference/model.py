from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import torch
import os

class ChronosInference:
    def __init__(self, model_path="/app/model_data"):
        self.model_path = model_path
        self.predictor = None
        
    def train(self, train_data: TimeSeriesDataFrame):
        """
        AutoGluon Integration: Initialize the training loop using autogluon.timeseries with 
        presets="chronos2", fine_tune=True, fine_tune_mode="lora", cross_learning=True.
        Device map = cuda.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.predictor = TimeSeriesPredictor(
            prediction_length=1, 
            target="target",
            path=self.model_path,
            quantile_levels=[0.1, 0.5, 0.9],
            known_covariates_names=[],
            freq="B"
        ).fit(
            train_data,
            presets="chronos2",
            hyperparameters={
                "Chronos2": {
                    "model_path": "amazon/chronos-2",
                    "fine_tune": True,
                    "fine_tune_mode": "lora",
                    "cross_learning": True,
                    "fine_tune_lora_config": {
                        "r": 8,
                        "lora_alpha": 16,
                        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "output_patch_embedding.output_layer"]
                    }
                }
            }
        )

    def load(self):
        if os.path.exists(self.model_path):
            self.predictor = TimeSeriesPredictor.load(self.model_path)
        else:
            print(f"Warning: Model path {self.model_path} does not exist. Pre-load bypassed.")
            
    def predict(self, context_data: TimeSeriesDataFrame):
        """
        Given the 100-day padded context, predicts the next step expecting quantiles 0.1, 0.5, 0.9
        """
        if self.predictor is None:
            self.load()
            
        if self.predictor is None:
            raise RuntimeError("Model is not loaded or trained yet.")
            
        return self.predictor.predict(context_data)
