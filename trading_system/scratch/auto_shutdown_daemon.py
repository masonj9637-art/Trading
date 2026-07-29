import time
import os
import subprocess
import sys

pid = 8178
log_file = "/home/mason/Trading/logs/auto_shutdown.log"

with open(log_file, "a") as f:
    f.write(f"[{time.ctime()}] Monitoring PID {pid} for automatic PC shutdown...\n")
    f.flush()

while True:
    try:
        os.kill(pid, 0)
    except OSError:
        with open(log_file, "a") as f:
            f.write(f"[{time.ctime()}] PID {pid} finished. Waiting 10 seconds before powering off PC...\n")
            f.flush()
        time.sleep(10)
        subprocess.run([
            "dbus-send", "--system", "--print-reply", 
            "--dest=org.freedesktop.login1", 
            "/org/freedesktop/login1", 
            "org.freedesktop.login1.Manager.PowerOff", 
            "boolean:true"
        ])
        break
    time.sleep(5)
