import subprocess
import time
import os
import sys
import datetime
import json
import zoneinfo
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

STATE_FILE = '.run_state.json'

def get_run_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_morning_run": "", "last_afternoon_run": ""}

def save_run_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def run_command(cmd, capture=False):
    print(f"Running command: {' '.join(cmd)}")
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True)
    else:
        return subprocess.run(cmd)

def main():
    # 1. Start up the trading engine docker container
    print("Step 1: Starting up the trading engine docker container...")
    res = run_command(["docker", "compose", "up", "-d"])
    if res.returncode != 0:
        print("Error: Failed to start docker containers.")
        sys.exit(res.returncode)

    # 2. Wait for the inference server to load
    print("Step 2: Waiting for the inference server to load...")
    server_ready = False
    import urllib.request
    for i in range(30):
        try:
            response = urllib.request.urlopen("http://localhost:8000/docs", timeout=2)
            if response.status == 200:
                server_ready = True
                print("Inference server is ready.")
                break
        except Exception:
            pass
        time.sleep(1)

    if not server_ready:
        print("Error: Inference server failed to load within 30 seconds.")
        sys.exit(1)

    # Load environment variables manually
    try:
        with open('.env') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    os.environ[k] = v
    except Exception as e:
        print(f"Could not load .env: {e}")

    api_key = os.getenv('ALPACA_API_KEY', '')
    secret_key = os.getenv('ALPACA_SECRET_KEY', '')

    if not api_key or not secret_key:
        print("Error: ALPACA_API_KEY or ALPACA_SECRET_KEY not found in environment.")
        sys.exit(1)

    client = TradingClient(api_key, secret_key, paper=True)

    # Check if market is open before proceeding
    print("Checking if market is open...")
    clock = client.get_clock()
    if not clock.is_open:
        wait_seconds = (clock.next_open - clock.timestamp).total_seconds()
        
        # If the market opens in more than 2 hours, it's likely a weekend or holiday.
        if wait_seconds > 7200:
            print(f"Market is not opening soon ({wait_seconds/3600:.1f} hours away). Aborting to prevent overlapping runs.")
            sys.exit(0)
            
    # Wait until 9:45 AM EST
    ny_tz = zoneinfo.ZoneInfo("America/New_York")
    now_ny = datetime.datetime.now(ny_tz)
    target_time_ny = now_ny.replace(hour=9, minute=45, second=0, microsecond=0)
    
    if now_ny < target_time_ny:
        wait_seconds = (target_time_ny - now_ny).total_seconds()
        print(f"Waiting {wait_seconds:.0f} seconds until 9:45 AM EST for market volatility to settle...")
        time.sleep(max(0, wait_seconds))
        print("Market is now open and settled.")
    # 3. Execute the daily trading loop
    ny_tz = zoneinfo.ZoneInfo("America/New_York")
    now_ny = datetime.datetime.now(ny_tz)
    today_str = now_ny.strftime('%Y-%m-%d')
    
    state = get_run_state()
    
    if state.get("last_morning_run") == today_str:
        print("Morning loop already executed today. Skipping Step 3 and 4.")
    else:
        print("Step 3: Executing the daily trading loop...")
        res = run_command(
            ["docker", "compose", "exec", "-T", "trading-engine", "python", "main.py"],
            capture=True
        )
        print("--- Daily Loop Output ---")
        print(res.stdout)
        if res.stderr:
            print("--- Daily Loop Error ---")
            print(res.stderr)
    
        if res.returncode != 0:
            print(f"Error: Daily trading loop failed with exit code {res.returncode}")
            sys.exit(res.returncode)
            
        state["last_morning_run"] = today_str
        save_run_state(state)
    
        # 4. Verify that the Alpaca orders went through successfully
        print("Step 4: Checking Alpaca orders placed today...")
    
        now = datetime.datetime.now(datetime.timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
        req = GetOrdersRequest(
            status=QueryOrderStatus.ALL,
            limit=50,
            after=today_start
        )
        orders = client.get_orders(filter=req)
    
        print(f"\nAlpaca Orders placed today ({now.date()} UTC):")
        if not orders:
            print("No orders placed today.")
        else:
            for o in orders:
                print(f"- Symbol: {o.symbol}, Side: {o.side}, Qty: {o.qty}, Status: {o.status}, Avg Price: {o.filled_avg_price or 'N/A'}")

    # 5. OFI liquidation disabled temporarily.
    print("OFI agent is temporarily silenced. Exiting without afternoon wait.")

if __name__ == "__main__":
    main()
