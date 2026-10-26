"""Money helpers used by the invoice code."""


def round_cents(amount):
    """Round a float amount to cents."""
    return round(amount, 2)


def apply_discount(amount, pct):
    """Apply a percentage discount and round to cents."""
    return round_cents(amount * (1 - pct / 100))
