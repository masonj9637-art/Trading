from sklearn.decomposition import PCA
import numpy as np
import pandas as pd

class PCAOrthogonalizer:
    def __init__(self, n_components=3):
        self.n_components = n_components
        self.pca = PCA(n_components=self.n_components)
        
    def orthogonalize(self, returns_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a DataFrame of returns (dates as index, assets as columns).
        Extracts systematic beta via PCA and returns the idiosyncratic residual returns matrix E.
        E = X - reconstruct
        """
        # Fill NaNs with 0 for PCA computation
        X = returns_matrix.fillna(0).values
        
        # Ensure we don't try to extract more components than we have assets or samples
        actual_components = min(self.n_components, X.shape[0], X.shape[1])
        self.pca = PCA(n_components=actual_components)
        
        # Extract systematic components
        scores = self.pca.fit_transform(X)
        
        # Reconstruct systematic returns
        reconstructed = self.pca.inverse_transform(scores)
        
        # Calculate idiosyncratic residual returns
        residuals = X - reconstructed
        
        # Restore NaNs where they originally existed
        residuals_df = pd.DataFrame(residuals, index=returns_matrix.index, columns=returns_matrix.columns)
        residuals_df[returns_matrix.isna()] = np.nan
        
        return residuals_df
