# Isolate path policy state while preserving legacy calls
Refactor task.py so `Policy(rules=())` instances own their rules. Preserve module
functions `add(pattern, allow)`, `check(path)`, `reset()` via `default_policy`.
Policy exposes those methods plus `rules()` returning a fresh list of pairs.
Patterns/paths are POSIX-style relative strings: collapse repeated '/' and '.';
reject absolute paths and ANY '..' segment with ValueError. A pattern may contain
`*` (one segment, including empty only if the entire path is empty) and `**`
(zero or more segments), each only as a whole segment; other embedded '*' is
invalid. Empty normalized pattern matches only empty path. Case sensitive.
Rules checked in insertion order, LAST matching rule wins; no match means False.
add validates pattern and requires bool allow, else ValueError without mutation.
Constructor accepts iterable of pairs, reset clears only that instance. Rules
returns normalized patterns. Preserve legacy functions' results for valid input.
Use fnmatch or your own matching but '*' must not cross slash boundaries.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
