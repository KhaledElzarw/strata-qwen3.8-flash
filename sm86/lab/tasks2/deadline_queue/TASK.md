# Repair a reschedulable deadline queue
Fix `Queue(clock)`. `schedule(key, when, value)` inserts or replaces a key.
`cancel(key)` returns True if pending, else False. `pop_due(limit=None)` returns
`(key, value)` pairs due at when <= clock(), ordered by deadline then scheduling
sequence. Every replacement gets a NEW sequence even when its deadline stays
the same. A stale heap entry must never release a replacement early or twice.
limit None means unlimited; nonnegative integer limit caps returned live items,
not stale heap entries. Negative limit raises ValueError without changes.
`peek()` returns earliest live `(key, when)` or None, even if not due.
`len(queue)` counts live keys. Values and keys may be mutually unorderable
hashable objects, so never compare them for ordering. clock is injected and
pop_due reads it once. cancel and peek must ignore stale heap entries.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
