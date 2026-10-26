from pkg.parse import parse


def test_parse_splits_words():
    assert parse("a b") == ["a", "b"]
