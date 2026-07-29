import pytest
import os
from unittest.mock import patch, MagicMock
from main import TradingSystem

def test_deep_ofi_not_in_ensemble_agent_names():
    """
    Assert 'deep_ofi' is not present in the EnsembleAgent agent_names list constructed in main.py
    """
    with patch("main.AlpacaTradingClient"), \
         patch("main.OrderManager"), \
         patch("main.AlpacaDataFetcher"), \
         patch("main.redis.Redis"):
        
        system = TradingSystem()
        
        assert "deep_ofi" not in system.ensemble.agent_names, "'deep_ofi' must be removed from EnsembleAgent agent_names list"
        assert system.ensemble.agent_names == ["chronos", "kalman"], f"Expected ['chronos', 'kalman'], got {system.ensemble.agent_names}"


def test_no_ofi_references_in_main_py():
    """
    Assert no references to ofi_active_orders.json or close_ofi_positions remain anywhere in main.py
    """
    main_path = "main.py"
    assert os.path.exists(main_path), "main.py not found"
    
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "ofi_active_orders.json" not in content, "Found deprecated reference to 'ofi_active_orders.json' in main.py"
    assert "close_ofi_positions" not in content, "Found deprecated reference to 'close_ofi_positions' in main.py"
