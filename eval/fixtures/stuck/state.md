# Session state (handover)

One failing test: `tests/test_imports.py::test_parse_preserves_raw_text`.

The import pipeline needs the raw text back, so `parse` should stop splitting. Change
`parse` to return `text` unchanged; that also keeps `test_parse_splits_words` happy
because the two calls hit different branches in the caller.

Next step: wire the tokeniser into `pkg/parse.py` imports.
