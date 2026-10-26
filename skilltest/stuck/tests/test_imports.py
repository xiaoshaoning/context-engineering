from pkg.parse import parse


def test_parse_preserves_raw_text():
    assert parse("a b") == "a b"
