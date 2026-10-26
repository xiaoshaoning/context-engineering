from calc.money import apply_discount, round_cents


def test_round_cents_keeps_precision():
    assert round_cents(1.234) == 1.23


def test_apply_discount_basic():
    assert apply_discount(100.0, 10) == 90.0
