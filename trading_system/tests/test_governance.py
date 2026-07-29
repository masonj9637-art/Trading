import pandas as pd
from governance.firewall import GovernanceEngine

def test_quantile_fan_var_scaling():
    engine = GovernanceEngine(var_limit=0.05, global_max_leverage=1.0, chronos_max_concentration=1.0)
    
    proposed_weights = pd.Series({"AAPL": 0.5, "MSFT": -0.5})
    
    # AAPL has narrow envelope (W=0.02), MSFT has wide envelope (W=0.06 > 0.05 var_limit)
    quantile_preds = pd.DataFrame({
        '0.1': [0.01, -0.04],
        '0.5': [0.02, 0.00],
        '0.9': [0.03, 0.02] # AAPL W=0.02, MSFT W=0.06
    }, index=["AAPL", "MSFT"])
    
    raw_agent_weights = {
        'chronos': proposed_weights,
        'deep_ofi': pd.Series({"AAPL": 0.0, "MSFT": 0.0}),
        'kalman': pd.Series({"AAPL": 0.0, "MSFT": 0.0})
    }
    trust_weights = {
        'chronos': 1.0,
        'deep_ofi': 0.0,
        'kalman': 0.0
    }
    
    approved, constrained = engine.evaluate_trades(raw_agent_weights, trust_weights, quantile_preds, account_nav=100000.0)
    
    # AAPL W=0.02 < 0.05 limit, should not scale down
    assert approved["AAPL"] == 0.5
    
    # MSFT W=0.06 > 0.05 limit. Scale factor = max(0, 1 - 0.06/0.05) = max(0, 1 - 1.2) = 0. Blocked.
    assert approved["MSFT"] == 0.0


def test_governance_engine_conservative_defaults():
    """
    Assert that instantiating GovernanceEngine() with no arguments produces the new
    conservative defaults, not the old Optuna-derived overfit values.
    """
    engine = GovernanceEngine()
    
    # Verify new conservative defaults
    assert engine.var_limit == 0.05
    assert engine.global_max_leverage == 1.5
    assert engine.global_max_drawdown == 0.10
    assert engine.agent_concentration_limits['deep_ofi'] == 0.15
    assert engine.agent_concentration_limits['kalman'] == 0.15
    assert engine.agent_concentration_limits['chronos'] == 0.15
    
    # Assert old Optuna-derived overfit values never appear as defaults
    assert engine.var_limit != 0.0393
    assert engine.global_max_leverage != 1.9767
    assert engine.global_max_drawdown != 0.0984
    assert engine.agent_concentration_limits['deep_ofi'] != 0.3934
    assert engine.agent_concentration_limits['kalman'] != 0.1982
    assert engine.agent_concentration_limits['chronos'] != 0.1982


def test_drawdown_circuit_breaker_edge_cases():
    """
    Test drawdown circuit breaker edge cases: account_nav exactly at the drawdown threshold,
    just above it, and just below it.
    """
    engine = GovernanceEngine(global_max_drawdown=0.10)
    peak_nav = 100000.0
    # Threshold = 100000.0 * (1 - 0.10) = 90000.0
    
    raw_agent_weights = {
        'chronos': pd.Series({"AAPL": 0.10}),
        'kalman': pd.Series({"AAPL": 0.0})
    }
    trust_weights = {'chronos': 1.0, 'kalman': 0.0}
    
    # Case 1: Just above threshold (90000.01) -> Circuit breaker inactive
    res_above = engine.evaluate_trades(raw_agent_weights, trust_weights, None, account_nav=90000.01, peak_nav=peak_nav)
    approved_above = res_above[0] if isinstance(res_above, tuple) else res_above
    assert approved_above["AAPL"] == 0.10, "Circuit breaker should not trigger when NAV is strictly above threshold"
    
    # Case 2: Exactly at threshold (90000.00) -> Circuit breaker inactive
    res_at = engine.evaluate_trades(raw_agent_weights, trust_weights, None, account_nav=90000.00, peak_nav=peak_nav)
    approved_at = res_at[0] if isinstance(res_at, tuple) else res_at
    assert approved_at["AAPL"] == 0.10, "Circuit breaker should not trigger when NAV is exactly at threshold"
    
    # Case 3: Just below threshold (89999.99) -> Circuit breaker active (all trades halted)
    res_below = engine.evaluate_trades(raw_agent_weights, trust_weights, None, account_nav=89999.99, peak_nav=peak_nav)
    approved_below = res_below[0] if isinstance(res_below, tuple) else res_below
    assert approved_below["AAPL"] == 0.0, "Circuit breaker must trigger and halt trades when NAV is strictly below threshold"
