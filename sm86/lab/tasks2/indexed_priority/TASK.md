# Repair stable indexed priority updates
Fix `Priority`. `put(key, priority, value)` inserts or updates. Items pop in
ascending numeric priority order, ties by FIRST insertion order. Updates keep
that order; removal followed by reinsertion gets new order. `pop()` returns
`(key, value)` and removes it, or raises KeyError when empty. `peek()` is the same
without removal. `remove(key)` returns bool; `len(queue)` counts live items.
Keys are arbitrary hashable objects, values arbitrary objects; neither may be
compared to break ties. Obsolete heap records from updates/removal must never
resurrect an entry or pop its replacement incorrectly. Empty peek raises
KeyError too. Independent instances share no state.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
