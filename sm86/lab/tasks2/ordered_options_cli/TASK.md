# Ordered configuration operations CLI
Extend task.py, run as `python task.py [--set KEY=JSON] [--unset KEY] [--append
KEY=JSON] [--pretty]`. Stdin is one JSON object (empty/whitespace stdin means {}).
Operations may repeat and MUST apply in original argument order across flags.
KEY is dot-separated segments matching `[A-Za-z_][A-Za-z0-9_]*`. set creates
missing parent dicts and replaces the final value. unset removes existing final
key, ignores missing path, but scalar/list parent is an error. append creates a
missing final list, appends ONE JSON value; nonlist final or nondict parent errors.
Missing parents for append are created like set. set/unset legacy behavior stays.
Argument syntax, invalid KEY/JSON, unknown flags or missing option values give
argparse usage error 2. Invalid/nonobject stdin or applying an operation through
a nondict gives stderr `error: data` and returns 1, no stdout. Output one JSON
object plus LF, keys sorted, ensure_ascii=False; compact separators by default,
indent=2 with --pretty. No operations still normalizes input. Buffer output.
main(argv=None, stdin=None) may raise SystemExit for usage; import has no effects.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
