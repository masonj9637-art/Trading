import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock
from main import resolve_peak_nav


def test_drawdown_persistence_redis_unavailable_disk_fallback():
    """
    Simulate Redis being unavailable (None or throwing exception) or returning no stored peak,
    and assert peak_nav still correctly resolves to the true historical high-water mark via the
    disk-backed fallback, not the current account value.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump({"peak_nav": 150000.0}, tmp)
        tmp_path = tmp.name
        
    try:
        account_nav = 100000.0 # Current account NAV is lower than historical peak
        
        # 1. Redis is None
        resolved_peak = resolve_peak_nav(account_nav, redis_client=None, peak_file_path=tmp_path)
        assert resolved_peak == 150000.0, f"Expected 150000.0 from disk fallback, got {resolved_peak}"
        assert resolved_peak != account_nav, "peak_nav should not default to current account value when disk backup exists"
        
        # 2. Redis throws Exception
        failing_redis = MagicMock()
        failing_redis.get.side_effect = Exception("Redis Connection Refused")
        resolved_peak_err = resolve_peak_nav(account_nav, redis_client=failing_redis, peak_file_path=tmp_path)
        assert resolved_peak_err == 150000.0, f"Expected 150000.0 from disk fallback when Redis fails, got {resolved_peak_err}"
        
        # 3. Redis returns None
        empty_redis = MagicMock()
        empty_redis.get.return_value = None
        resolved_peak_empty = resolve_peak_nav(account_nav, redis_client=empty_redis, peak_file_path=tmp_path)
        assert resolved_peak_empty == 150000.0, f"Expected 150000.0 from disk fallback when Redis returns None, got {resolved_peak_empty}"
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
