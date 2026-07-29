import re

dates = []
with open('eod_audit.log', 'r') as f:
    lines = f.readlines()

current_date = None
for line in lines:
    m = re.search(r"EOD AUDIT REPORT - (\d{4}-\d{2}-\d{2})", line)
    if m:
        current_date = m.group(1)
    
    m2 = re.search(r"Daily PnL: (.*?)\s*\(", line)
    if m2 and current_date:
        pnl = m2.group(1).strip()
        print(f"{current_date}: {pnl}")
