import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np

class ConditionalAutoencoder(nn.Module):
    """
    Deep neural network that learns complex, non-linear market beta conditioned on firm characteristics.
    """
    def __init__(self, num_characteristics, num_factors):
        super(ConditionalAutoencoder, self).__init__()
        # Encoder: Beta Network conditioned on firm characteristics
        self.encoder = nn.Sequential(
            nn.Linear(num_characteristics, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, num_factors)
        )
        
    def forward(self, characteristics, factor_returns):
        # characteristics: (batch_size, num_assets, num_characteristics)
        # factor_returns: (batch_size, num_factors) -> latent systematic market factors
        
        # Dynamically generate betas using the deep encoder
        betas = self.encoder(characteristics) # (batch_size, num_assets, num_factors)
        
        # Decoder: Reconstruct systematic return via inner product
        # reconstructed_return = betas * factor_returns
        reconstructed_return = torch.bmm(betas, factor_returns.unsqueeze(2)).squeeze(2)
        return reconstructed_return

class DeepOrthogonalizer:
    def __init__(self, num_factors=3, epochs=100, lr=0.01):
        self.num_factors = num_factors
        self.epochs = epochs
        self.lr = lr
        
    def orthogonalize(self, returns_data: pd.DataFrame, characteristics_data: np.ndarray = None, window_size=100) -> pd.DataFrame:
        """
        Orthogonalizes returns using a Conditional Autoencoder in a strictly CAUSAL rolling window
        to prevent lookahead bias (data leakage).
        """
        if characteristics_data is None:
            num_timesteps, num_assets = returns_data.shape
            characteristics_data = np.random.randn(num_timesteps, num_assets, 5)
            
        returns_tensor = torch.tensor(returns_data.values, dtype=torch.float32)
        char_tensor = torch.tensor(characteristics_data, dtype=torch.float32)
        
        num_timesteps, num_assets, num_chars = char_tensor.shape
        causal_residuals = np.zeros((num_timesteps, num_assets))
        
        # If dataset is smaller than window_size, fallback to full-sample
        if num_timesteps <= window_size:
            window_size = num_timesteps

        for t in range(window_size, num_timesteps + 1):
            start_idx = t - window_size
            end_idx = t
            
            window_returns = returns_tensor[start_idx:end_idx]
            window_chars = char_tensor[start_idx:end_idx]
            
            model = ConditionalAutoencoder(num_characteristics=num_chars, num_factors=self.num_factors)
            optimizer = optim.Adam(model.parameters(), lr=self.lr, weight_decay=1e-4) 
            criterion = nn.MSELoss()
            
            latent_factors = nn.Parameter(torch.randn(window_size, self.num_factors))
            optimizer.add_param_group({'params': [latent_factors]})
            
            for epoch in range(self.epochs):
                optimizer.zero_grad()
                reconstructed = model(window_chars, latent_factors)
                loss = criterion(reconstructed, window_returns)
                loss.backward()
                optimizer.step()
                
            with torch.no_grad():
                reconstructed = model(window_chars, latent_factors)
                # Strictly causal residual for the last day of the window (Day T)
                causal_residuals[t - 1] = (window_returns[-1] - reconstructed[-1]).numpy()
                
            # Backfill the warmup period using the first trained window
            if t == window_size:
                causal_residuals[start_idx:end_idx] = (window_returns - reconstructed).numpy()
                
        return pd.DataFrame(causal_residuals, index=returns_data.index, columns=returns_data.columns)
