from pkg.mod_07 import op_07_01


def test_sum():
    assert op_07_01([{"amount": 2}, {"amount": 3}]) == 5
