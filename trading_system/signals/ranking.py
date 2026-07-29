import pandas as pd

class PortfolioRanker:
    def rank_and_normalize(self, alpha_signals: pd.DataFrame) -> pd.DataFrame:
        """
        Translates alpha signals into a dollar-neutral Long/Short portfolio by ranking assets cross-sectionally.
        Calculates raw unnormalized weights using a ranking operator: w = Rank(signal) - N/2
        Normalizes them to ensure gross exposure equals 1.0x.
        """
        # Rank cross-sectionally across assets (columns) for each day (row)
        ranks = alpha_signals.rank(axis=1, method='average')
        
        # Number of non-NaN assets per day
        N = alpha_signals.notna().sum(axis=1)
        
        # Raw weights: w = rank - N/2
        # Use .sub() with axis=0 to subtract the series N/2 from each column
        raw_weights = ranks.sub(N / 2.0, axis=0)
        
        # Normalize: w_hat = w / sum(|w|)
        sum_abs_weights = raw_weights.abs().sum(axis=1)
        
        # Divide by sum of absolute weights to enforce 1.0x gross leverage
        normalized_weights = raw_weights.div(sum_abs_weights, axis=0)
        
        # Fill completely NaN rows with 0
        return normalized_weights.fillna(0)
