import os
import sys
import psutil
import subprocess
from datetime import datetime

LOG_FILE = "/home/mason/Trading/monitor_memory.log"
TRADING_DIR = "/home/mason/Trading"

def log_state(state, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {state} - {details}\n"
    print(full_msg.strip())
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        if lines:
            last_line = lines[-1]
            if "] " in last_line:
                last_content = last_line.split("] ", 1)[1]
                if last_content.startswith(state + " -"):
                    lines[-1] = full_msg
                    with open(LOG_FILE, "w") as f:
                        f.writelines(lines)
                    return

        with open(LOG_FILE, "a") as f:
            f.write(full_msg)
    except Exception as e:
        print(f"Failed to write to log: {e}")

def run_cmd(cmd):
    return subprocess.run(cmd, cwd=TRADING_DIR, capture_output=True, text=True)

def check_health():
    mem = psutil.virtual_memory()
    mem_percent = mem.percent

    if mem_percent > 85.0:
        log_state("WARNING_RAM", f"RAM at {mem_percent}%. Restarting trading-engine...")
        run_cmd(["docker", "compose", "restart", "trading-engine"])
        return

    res = run_cmd(["docker", "compose", "ps", "--services", "--filter", "status=running"])
    if "trading-engine" not in res.stdout:
        log_state("WARNING_CONTAINER", "trading-engine is down! Attempting to start...")
        run_cmd(["docker", "compose", "up", "-d"])
    else:
        log_state("NORMAL", f"Health check passed. RAM: {mem_percent}%")

if __name__ == "__main__":
    check_health()
