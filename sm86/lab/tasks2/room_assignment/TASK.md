# Repair room assignment
Fix `assign(bookings)` and `conflicts(bookings)` in `task.py`. Bookings are an
iterable of `(id, start, end)` with distinct string IDs and integer times.
Reversed ranges or repeated IDs raise ValueError, including repeated empty
bookings. Inputs are never changed. Empty bookings receive room None and cause
no conflicts. Process nonempty bookings by `(start, end, id)`; reuse the smallest
available nonnegative room number, and a room is free at its previous end time.
`assign` returns a dict from every ID to its room. `conflicts` returns all
lexicographically sorted `(smaller_id, larger_id)` pairs whose nonempty
half-open intervals overlap. Touching intervals do not conflict.

Add utilization(bookings): return dict room -> sum of durations assigned to it
under assign's policy. Empty bookings contribute nothing; no rooms gives {}.
Consume the iterable once, validate identically and never change inputs.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
