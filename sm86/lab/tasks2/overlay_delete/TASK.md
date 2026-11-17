# Repair layered object overlays
Fix `merge(base, layers)` for JSON-like values. Each layer is a dict. At a dict
key, the exact object `{'$delete': True}` deletes the key, without error if absent.
No other object is a deletion marker (in particular integer 1 is not True).
When old and new values are BOTH dicts, merge recursively; otherwise replace
with a deep copy, but a dict replacing a nondict is recursively interpreted
against an empty dict (so nested delete markers still apply). Lists replace
wholesale; markers inside lists are ordinary data. At the root base must be a
dict and layers must contain dicts, else ValueError. Layers apply in order.
Inputs and every returned mutable object are independent; no input mutation.
Keys are strings. Empty layers preserve a deep copy of base.

Add explain(base, layers) returning (merged, history), where history is a list
per layer of sorted changed key-path tuples. Compare recursively, type-strictly:
if both values are dicts recurse; otherwise emit that path when changed.
Adding/removing a dict emits its parent path only. No-op layers give [].
Lists are atomic, including nested bool/int differences. No input mutation.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
