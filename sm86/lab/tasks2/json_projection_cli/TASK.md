# JSON lines projection CLI
Implement task.py, run as `python task.py FIELD [--missing skip|null|error]
[--where KEY=JSON]`. FIELD and KEY are dot-separated nonempty dict keys; empty
segments raise argparse usage error (exit 2). No list traversal. Read UTF-8 JSON
objects one per nonblank stdin line, with physical line numbers including blanks.
--where may repeat and all equality filters apply; compare recursive type-strict
JSON equality, and missing filter keys never match. Malformed KEY=JSON is usage
error 2. Parse/validate every input line even if filtered out. Nonobject or invalid
JSON gives stderr `error: line N` and exit 1. Output selected FIELD as compact
JSON, ensure_ascii=False, one per LF. Missing projected field defaults to skip;
null emits null; error gives same line diagnostic. Buffer ALL output until every
line succeeds: data error prints no stdout. Empty input succeeds. `main(argv=None,
stdin=None)` returns status (argparse may raise SystemExit); import has no effects.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
