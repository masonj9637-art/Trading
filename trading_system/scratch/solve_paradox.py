def test_all():
    for current_qty in [-43.0, 43.0, 0.0, -86.0, 86.0]:
        for others_target_qty in [-90.46, -4.46, 4.46, 90.46]:
            delta_qty = others_target_qty - current_qty
            abs_delta = abs(delta_qty)
            action = 'BUY' if delta_qty > 0 else 'SELL'
            target_qty = current_qty + delta_qty
            
            crossed = False
            if current_qty != 0 and (target_qty * current_qty < 0):
                crossed = True
                
            if not crossed and action == 'BUY' and round(abs_delta) == 47:
                print(f"MATCH! current_qty={current_qty}, others_target_qty={others_target_qty}, delta_qty={delta_qty}")

test_all()
