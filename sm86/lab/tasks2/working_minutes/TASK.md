# Working minutes with closures
Extend `Calendar` in `task.py` with blackout support and `advance`. Times and
lengths are integers. Constructor `Calendar(windows, blackouts=())` normalizes
half-open windows: drop empty ranges and merge overlap or touching endpoints.
Subtract the union of blackouts; reversed ranges anywhere raise ValueError.
`spans()` returns a fresh sorted list of resulting nonempty pairs.
`remaining(t)` counts working minutes at or after t.
`advance(t, minutes)` consumes working time starting at the first working instant
at or after t, skipping gaps. Negative minutes raise ValueError. Zero returns t
unchanged, even outside working time. Positive requests ending exactly at a span
end return that end, without jumping the next gap. Insufficient time raises
ValueError. Construction consumes each iterable once and no caller data is
mutated. Preserve the existing union and remaining behavior without blackouts.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
