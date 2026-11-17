# Reconcile keyed records with renames
Extend `reconcile(old, new, renames=None)`. old/new are lists of dicts containing
unique string `id` fields, else ValueError. Return a list of operations:
`('remove', id)`, `('rename', old_id, new_id)`, `('update', id, changes)`, and
`('add', record)`. renames maps old IDs to distinct new IDs. Every source must
exist in old and every target in new; invalid maps raise ValueError. A target
may not collide with ANY different old ID, even one removed or renamed, so swaps
are invalid. Identity renames are allowed and emit nothing. Match renamed old
records to target IDs. First emit unmatched removals sorted by old ID, then
nonidentity renames sorted by source, then updates sorted by target ID, then
adds sorted by id. changes maps changed non-id fields to deep-copied new values;
removed fields map to `{'$missing': True}`. Compare nested values type-strictly
(True differs from 1 at any depth). Records may use any JSON-like values except
the reserved missing marker as field values. Neither input nor output shares
mutable values. Existing add/remove/update behavior with no renames stays.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
