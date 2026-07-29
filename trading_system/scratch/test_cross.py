current_qty = 8.0
delta_qty = -10.2754
target_qty = current_qty + delta_qty

print(f"current: {current_qty}, delta: {delta_qty}, target: {target_qty}")
if current_qty != 0 and (target_qty * current_qty < 0):
    print("Crossing zero!")
else:
    print("Not crossing zero!")
