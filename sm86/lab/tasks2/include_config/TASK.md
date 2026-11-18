# Configuration includes and deferred references
Implement `load(files, entry)` in `task.py`; files maps names to text, with no
filesystem access. Each stripped nonblank line is either `#` comment, `@include NAME`
(NAME is a nonempty string without whitespace), or `KEY = VALUE`. KEY matches
`[A-Za-z_][A-Za-z0-9_]*`. VALUE is stripped text, possibly empty; # inside a value
is literal. Includes expand at their position; later definitions overwrite earlier
ones globally, including across files. Missing files raise KeyError. An include
cycle raises ValueError, but including the same file again off the active stack
is allowed. Validate every expanded line even if a later line overwrites it.
After all definitions are collected, expand `${KEY}` references against FINAL
values, recursively. Forward references work. Missing referenced keys raise
KeyError; reference cycles raise ValueError. `$$` emits a literal dollar and
prevents that dollar from starting a reference. Other dollars are literal unless
followed by `{`; malformed `${...}` raises ValueError (key grammar as above).
Return a new dict of strings; do not modify files. Only surviving final values
are expanded. Implement both include and reference cycle detection.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
