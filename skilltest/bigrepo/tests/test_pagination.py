from pkg.mod_31 import page_slice


def test_first_page():
    items = list(range(25))
    assert page_slice(items, 1) == items[:10]


def test_second_page():
    items = list(range(25))
    assert page_slice(items, 2) == items[10:20]
