import numpy as np
import pandas as pd
import json

class EnsembleAgent:
    def __init__(self, agent_names, risk_penalty=2.0, discount_factor=0.95, redis_client=None):
        self.agent_names = agent_names
        self.risk_penalty = risk_penalty
        self.discount_factor = discount_factor
        self.redis_client = redis_client
        self.redis_key = "ensemble_posteriors"
        
        # Track expected return (mean) and variance for MVTS
        # Dict[regime][agent_name] = {'ewma': mean, 'ewmvar': variance, 'weight': sum_of_weights}
        self.posteriors = {
            'BULL_TREND': {name: {'ewma': 0.05, 'ewmvar': 0.001, 'weight': 1.0} for name in agent_names},
            'BEAR_TREND': {name: {'ewma': 0.05, 'ewmvar': 0.001, 'weight': 1.0} for name in agent_names},
            'CHOP': {name: {'ewma': 0.05, 'ewmvar': 0.001, 'weight': 1.0} for name in agent_names}
        }
        
        # Load from Redis if available
        if self.redis_client:
            try:
                stored = self.redis_client.get(self.redis_key)
                if stored:
                    self.posteriors = json.loads(stored)
                    print("Successfully restored Bayesian posteriors from Redis.")
            except Exception as e:
                print(f"Failed to load posteriors from Redis: {e}")
        
    def sample_trust_weights(self, regime: str) -> dict:
        """
        Executes Mean-Variance Thompson Sampling (MVTS) with Combinatorial Adaptive Discounting (CADTS).
        Returns normalized weights proportional to the sampled risk-adjusted returns.
        """
        sampled_scores = {}
        for name in self.agent_names:
            stats = self.posteriors[regime][name]
            mu = stats['ewma']
            var = stats['ewmvar']
            
            # Sample precision from Gamma and mean from Gaussian (simplified via direct sampling)
            # To keep it computationally fast for backtesting, we sample the MV objective directly
            # MV_i = mu_i - (rho) * var_i
            # We add exploration noise proportional to the variance
            exploration_noise = np.random.normal(0, np.sqrt(var) if var > 0 else 0.01)
            
            risk_adjusted_score = mu - (self.risk_penalty * var) + exploration_noise
            # Relu to ensure no negative weights
            sampled_scores[name] = max(0.001, risk_adjusted_score)
            
        total_score = sum(sampled_scores.values())
        return {name: score / total_score for name, score in sampled_scores.items()}
        
    def update_posteriors(self, regime: str, agent_performances: dict):
        """
        Updates the MVTS priors using CADTS geometric discounting based on continuous reward (IC/PnL).
        agent_performances: dict of {agent_name: realized_daily_continuous_reward}
        """
        for name, reward in agent_performances.items():
            stats = self.posteriors[regime][name]
            old_mu = stats['ewma']
            old_weight = stats['weight']
            
            # Geometric discounting (CADTS)
            new_weight = old_weight * self.discount_factor + 1.0
            
            # Incremental update of mean
            new_mu = old_mu + (reward - old_mu) / new_weight
            
            # Incremental update of variance (Welford's algorithm with discounting)
            old_var = stats['ewmvar']
            new_var = (old_var * old_weight * self.discount_factor + (reward - old_mu) * (reward - new_mu)) / new_weight
            
            self.posteriors[regime][name]['ewma'] = new_mu
            self.posteriors[regime][name]['ewmvar'] = max(1e-6, new_var) # Prevent zero variance
            self.posteriors[regime][name]['weight'] = new_weight
            
        if self.redis_client:
            try:
                self.redis_client.set(self.redis_key, json.dumps(self.posteriors))
            except Exception as e:
                print(f"Failed to save posteriors to Redis: {e}")
