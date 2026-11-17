# Coverage bands
Implement `bands(intervals, minimum=1)` in `task.py`. Each interval is an integer
half-open pair `(start, end)`. Reject reversed pairs and nonpositive minimum with
ValueError. Empty pairs contribute nothing. Duplicate intervals count separately.
Return sorted maximal `(start, end, count)` tuples where coverage is at least
minimum. Split whenever the count changes, but combine adjacent equal counts.
Events at the same endpoint happen together. Negative coordinates are valid.
Accept any iterable of pairs, consume it once, and never mutate caller data.
Implement `peak(intervals)` returning `(maximum_count, earliest_coordinate)`;
for no nonempty intervals return `(0, None)`. It uses the same validation.

Also implement first_window(intervals, length, minimum=1): earliest integer
start of a length-long continuous span meeting minimum, or None. length must
be positive (ValueError). Coverage count changes do not break continuity when
both counts meet minimum. Accept one-shot iterables and validate as bands.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
