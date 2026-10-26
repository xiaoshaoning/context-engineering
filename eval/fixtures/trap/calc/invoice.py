from calc.money import apply_discount


def line_total(unit_price, quantity):
    return unit_price * quantity


def invoice_total(lines, discount_pct=0):
    subtotal = sum(line_total(p, q) for p, q in lines)
    return apply_discount(subtotal, discount_pct)
