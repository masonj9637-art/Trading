import os
import re
import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

EXECUTION_LOG_PATH = "/home/mason/Trading/logs/daily_execution.log"
AUDIT_LOG_PATH = "/home/mason/Trading/eod_audit.log"

def run_audit():
    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    
    try:
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    os.environ[k] = v
    except Exception:
        pass

    api_key = os.getenv('ALPACA_API_KEY', '')
    secret_key = os.getenv('ALPACA_SECRET_KEY', '')
    
    if not api_key or not secret_key:
        print("ERROR: Missing Alpaca API keys.")
        return

    # 1. Parse local execution logs
    routing_attempts = 0
    discrepancies = []
    
    # Regex to match: 2026-06-26 09:30:37,474 [INFO] Routing SELL 12.5197 V [Non-OFI/GTC] via Alpaca...
    route_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+[\d:,]+\s+\[INFO\]\s+Routing\s+(BUY|SELL)\s+([\d.]+)\s+([A-Z.]+)")
    # Regex to match: 2026-06-26 09:30:37,521 [ERROR] Failed to route order to Alpaca: {"code":42210000,"message":"bracket orders must be entry orders"}
    error_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+[\d:,]+\s+\[ERROR\]\s+Failed to route order to Alpaca:\s+(.*)")
    
    last_routed_symbol = None
    last_routed_qty = None
    last_routed_action = None
    
    if os.path.exists(EXECUTION_LOG_PATH):
        with open(EXECUTION_LOG_PATH, 'r') as f:
            for line in f:
                if today_str in line:
                    route_match = route_pattern.search(line)
                    if route_match:
                        routing_attempts += 1
                        last_routed_action = route_match.group(2)
                        last_routed_qty = route_match.group(3)
                        last_routed_symbol = route_match.group(4)
                        continue
                        
                    err_match = error_pattern.search(line)
                    if err_match:
                        err_msg = err_match.group(2)
                        if last_routed_symbol:
                            discrepancies.append({
                                'symbol': last_routed_symbol,
                                'action': last_routed_action,
                                'qty': last_routed_qty,
                                'error': err_msg
                            })
                            # Clear it so we don't double count
                            last_routed_symbol = None
    
    # Prepare Audit Report String
    report_lines = []
    report_lines.append("==================================================")
    report_lines.append(f"EOD AUDIT REPORT - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("==================================================")
    report_lines.append(f"Local Execution Date Checked: {today_str}")
    report_lines.append(f"Total Local Routing Attempts: {routing_attempts}")
    report_lines.append("")
    
    for disc in discrepancies:
        report_lines.append(f"Checking local routing: {disc['action']} {disc['qty']} {disc['symbol']} at {today_str}")
        report_lines.append(f"  --> LOCAL ROUTING ERROR: Failed to route to Alpaca. Error: {disc['error']}")
        report_lines.append("")
        
    report_lines.append(f"Total Discrepancies Found: {len(discrepancies)}")
    for disc in discrepancies:
        report_lines.append(f"- [LOCAL_ROUTE_FAILURE] Symbol: {disc['symbol']} | Details: System attempted to route {disc['action']} {disc['qty']} {disc['symbol']} but failed locally with error: {disc['error']}")
    
    # 2. Fetch Today's Orders from Alpaca
    client = TradingClient(api_key, secret_key, paper=True)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    req = GetOrdersRequest(
        status=QueryOrderStatus.ALL,
        limit=500,
        after=today_start
    )
    orders = client.get_orders(filter=req)
    
    report_lines.append("")
    report_lines.append("=== WHAT ACTUALLY HAPPENED: TODAY'S ALPACA ORDERS ===")
    if not orders:
        report_lines.append("No orders were placed today.")
    else:
        for o in orders:
            report_lines.append(f"[{o.status.name}] {o.side.name} {o.qty} {o.symbol} @ {o.filled_avg_price or 'N/A'}")
            
    report_lines.append("")
    
    # 3. Get Account PnL
    try:
        account = client.get_account()
        equity = float(account.equity)
        last_equity = float(account.last_equity)
        pnl = equity - last_equity
        pnl_pct = (pnl / last_equity) * 100 if last_equity > 0 else 0
        
        report_lines.append("=== TODAY'S PNL ===")
        report_lines.append(f"Current Equity: ${equity:,.2f}")
        report_lines.append(f"Daily PnL: ${pnl:,.2f} ({pnl_pct:.2f}%)")
    except Exception as e:
        report_lines.append("=== TODAY'S PNL ===")
        report_lines.append(f"Failed to fetch PnL: {e}")
        
    report_lines.append("")
    
    full_report = "\n".join(report_lines)
    print(full_report)
    
    with open(AUDIT_LOG_PATH, 'a') as f:
        f.write(full_report + "\n")

if __name__ == "__main__":
    run_audit()
