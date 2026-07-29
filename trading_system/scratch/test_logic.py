current_qty = -43.0
others_target_qty = 4.4640
others_delta_qty = others_target_qty - current_qty

abs_delta = abs(others_delta_qty)
action = 'BUY' if others_delta_qty > 0 else 'SELL'
target_qty = current_qty + others_delta_qty

if current_qty != 0 and (target_qty * current_qty < 0):
    reduce_action = 'SELL' if current_qty > 0 else 'BUY'
    print(f"Routing {reduce_action} {abs(current_qty):.4f} [{action} - REDUCE]")
else:
    print(f"Routing {action} {abs_delta:.4f} [Non-OFI/GTC]")
