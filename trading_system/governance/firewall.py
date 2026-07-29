import pandas as pd
from typing import Dict, Optional
from .audit import AuditLogger

class GovernanceEngine:
    # Note: These default argument values are conservative, arbitrary placeholders.
    # They are not optimized risk limits. Any real risk parameters must be passed
    # explicitly by the caller after being validated on out-of-sample data.
    def __init__(self, 
                 var_limit=0.05, 
                 global_max_leverage=1.5, 
                 global_max_drawdown=0.10,
                 ofi_max_concentration=0.15,
                 kalman_max_concentration=0.15,
                 chronos_max_concentration=0.15):
        self.var_limit = var_limit
        self.global_max_leverage = global_max_leverage
        self.global_max_drawdown = global_max_drawdown
        self.agent_concentration_limits = {
            'deep_ofi': ofi_max_concentration,
            'kalman': kalman_max_concentration,
            'chronos': chronos_max_concentration
        }
        self.audit = AuditLogger()
        
    def evaluate_trades(self, raw_agent_weights: Dict[str, pd.Series], trust_weights: Dict[str, float], quantile_preds: Optional[pd.DataFrame], account_nav: float, peak_nav: float = None) -> pd.Series:
        """
        Applies agent-specific rules before blending, followed by global portfolio constraints.
        """
        # Rule 2/3: Max Drawdown Circuit Breaker
        if peak_nav is not None and account_nav < peak_nav * (1.0 - self.global_max_drawdown):
            self.audit.log("SYSTEM", f"CIRCUIT BREAKER: Max Drawdown breached. Halting all trades.")
            # Use any agent's index as base
            base_index = list(raw_agent_weights.values())[0].index
            return pd.Series(0, index=base_index), {}
            
        constrained_agent_weights = {}
        
        # Agent-Specific Constraints
        for agent_name, weights in raw_agent_weights.items():
            approved = weights.copy()
            max_conc = self.agent_concentration_limits.get(agent_name, 0.20)
            
            for asset, weight in approved.items():
                if weight == 0:
                    continue
                    
                # Position Sizing and Concentration Limits
                if abs(weight) > max_conc:
                    scale = max_conc / abs(weight)
                    approved[asset] *= scale
                    self.audit.log(asset, f"[{agent_name}] Scaled down concentration from {abs(weight):.2f} to {max_conc}")
                    
                # Signal Confidence Thresholds (VaR) - ONLY applied to Chronos
                if agent_name == 'chronos' and quantile_preds is not None and asset in quantile_preds.index:
                    q_low = quantile_preds.loc[asset, '0.1']
                    q_high = quantile_preds.loc[asset, '0.9']
                    W = abs(q_high - q_low)
                    
                    if W > self.var_limit:
                        scale_factor = max(0, 1 - (W / self.var_limit))
                        approved[asset] *= scale_factor
                        
                        if abs(approved[asset]) < 0.001:
                            approved[asset] = 0
                            
            constrained_agent_weights[agent_name] = approved
            
        # Blend constrained weights
        blended_weights = None
        for agent_name, weights in constrained_agent_weights.items():
            trust = trust_weights.get(agent_name, 0.0)
            if blended_weights is None:
                blended_weights = weights * trust
            else:
                blended_weights += weights * trust
                
        # Rule 1: Absolute Gross Leverage Check (Global)
        gross_exposure = blended_weights.abs().sum()
        if gross_exposure > self.global_max_leverage + 1e-6:
            scale = self.global_max_leverage / gross_exposure
            blended_weights *= scale
            for agent_name in constrained_agent_weights:
                constrained_agent_weights[agent_name] *= scale
            self.audit.log("PORTFOLIO", f"MODIFIED: Portfolio scaled down uniformly by {scale:.2f}x to meet max gross leverage of {self.global_max_leverage}x.")
            
        return blended_weights, constrained_agent_weights

