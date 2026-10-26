from calc.invoice import invoice_total


def test_simple_total():
    assert invoice_total([(10.0, 2), (5.5, 1)]) == 25.5


def test_invoice_total_is_rounded():
    assert invoice_total([(2.675, 1)]) == 2.68
