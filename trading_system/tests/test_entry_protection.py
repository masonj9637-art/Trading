import pytest
from unittest.mock import MagicMock, patch

def check_unprotected_positions(alpaca_client, alerter):
    """
    Replicates the unprotected position verification routine in main.py
    """
    from alpaca.trading.requests import GetOrdersRequest
    from alpaca.trading.enums import QueryOrderStatus
    
    check_positions = alpaca_client.get_open_positions()
    req = GetOrdersRequest(status=QueryOrderStatus.OPEN)
    open_orders = alpaca_client.client.get_orders(filter=req)
    open_order_symbols = {order.symbol for order in open_orders} if open_orders else set()
    
    unprotected_symbols = [
        pos.symbol for pos in check_positions 
        if abs(float(pos.qty)) >= 1.0 and pos.symbol not in open_order_symbols
    ]
    
    if unprotected_symbols:
        alert_msg = f"🚨 **UNPROTECTED POSITION WARNING:** The following open positions have no corresponding active OCO orders: {', '.join(unprotected_symbols)}"
        alerter.send_alert(alert_msg)
    return unprotected_symbols


def test_unprotected_position_alerting_path():
    """
    Simulate a position existing in get_open_positions() with no matching open OCO order,
    and assert the alerting path fires (mock discord_alerter and check it was called).
    """
    mock_position = MagicMock()
    mock_position.symbol = "AAPL"
    mock_position.qty = "10.0"
    
    mock_alpaca = MagicMock()
    mock_alpaca.get_open_positions.return_value = [mock_position]
    mock_alpaca.client.get_orders.return_value = [] # No matching open orders
    
    mock_alerter = MagicMock()
    
    unprotected = check_unprotected_positions(mock_alpaca, mock_alerter)
    
    # Assert unprotected symbol was identified
    assert unprotected == ["AAPL"]
    
    # Assert alerting path fired with expected alert message
    mock_alerter.send_alert.assert_called_once()
    alert_arg = mock_alerter.send_alert.call_args[0][0]
    assert "UNPROTECTED POSITION WARNING" in alert_arg
    assert "AAPL" in alert_arg


def test_protected_position_no_alert():
    """
    Simulate a position existing in get_open_positions() WITH a matching open OCO order,
    and assert the alerting path does not fire.
    """
    mock_position = MagicMock()
    mock_position.symbol = "MSFT"
    mock_position.qty = "5.0"
    
    mock_order = MagicMock()
    mock_order.symbol = "MSFT"
    
    mock_alpaca = MagicMock()
    mock_alpaca.get_open_positions.return_value = [mock_position]
    mock_alpaca.client.get_orders.return_value = [mock_order]
    
    mock_alerter = MagicMock()
    
    unprotected = check_unprotected_positions(mock_alpaca, mock_alerter)
    
    assert unprotected == []
    mock_alerter.send_alert.assert_not_called()
