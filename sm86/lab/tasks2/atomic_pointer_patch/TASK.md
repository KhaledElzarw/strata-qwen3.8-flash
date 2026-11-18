# Atomic pointer patch
Implement `apply(document, operations)` returning a deep-copied patched value;
never mutate document or operation values. Operations are dicts with `op`, `path`
and (for add/replace/test) `value`; remove needs no value. Paths are '' for root
or slash-separated JSON Pointer segments: ~0 decodes ~ and ~1 decodes /; any
other ~ escape raises ValueError. Dict keys are strings. List segments must be
canonical nonnegative decimal indexes (0 or nonzero digit followed by digits).
For add only, '-' appends and indexes through len(list) insert. Replace/remove/
test require existing items, raising KeyError for missing key or out-of-range
index. Traversing a scalar raises KeyError. Invalid paths/index syntax or unknown
ops raise ValueError. Root add/replace replaces document; root remove produces
None. test checks recursive type-strict equality (True differs from 1), raising
ValueError on mismatch. Apply operations sequentially; an error exposes no partial
mutation to caller. Extra operation fields are ignored. Inputs are JSON-like.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
