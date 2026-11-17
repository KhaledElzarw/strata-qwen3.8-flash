# Range map paint, erase and query
Extend `RangeMap` in task.py. Initially no integer points are assigned. `paint(lo,
hi, value)` assigns every point in half-open [lo,hi), overwriting prior values.
Add `erase(lo, hi)` which makes the range unassigned, and `query(lo, hi)` which
returns sorted clipped `(start, end, value)` spans of assigned points there.
`spans()` returns full maximal spans, combining adjacent equal values. Values
are strings or None; None is an ASSIGNED value, not an empty marker. All methods
with ranges reject lo > hi with ValueError and make no change; lo == hi does
nothing / returns []. `get(point, default=None)` returns assigned value or
default, preserving distinction via custom default. Negative coordinates work.
Do not enumerate points: bounds can exceed 10**12. Query/spans return fresh lists.
Keep paint/get compatibility; erase must split spans and queries must clip.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
