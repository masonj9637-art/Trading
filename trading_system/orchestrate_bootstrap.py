import subprocess
import time
import sys

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

    # 3. Execute the bootstrap model retraining
    print("Step 3: Executing the weekly model bootstrap retraining...")
    res = run_command(
        ["docker", "compose", "exec", "-T", "trading-engine", "python", "bootstrap_model.py"],
        capture=True
    )
    print("--- Bootstrap Output ---")
    print(res.stdout)
    if res.stderr:
        print("--- Bootstrap Error ---")
        print(res.stderr)

    if res.returncode != 0:
        print(f"Error: Bootstrap retraining failed with exit code {res.returncode}")
        sys.exit(res.returncode)

    # 4. Restart the inference server to load the new weights into VRAM
    print("Step 4: Restarting the inference server to load the new model weights...")
    res = run_command(["docker", "compose", "restart", "trading-engine"])
    if res.returncode != 0:
        print("Warning: Failed to restart the trading-engine container.")

    print("Weekly bootstrap retraining complete.")

if __name__ == "__main__":
    main()
