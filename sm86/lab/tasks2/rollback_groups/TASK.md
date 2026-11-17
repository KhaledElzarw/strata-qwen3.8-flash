# Rollback connectivity groups
Implement `Groups(items)` for distinct hashable items (duplicates raise ValueError).
`union(a,b)` returns True if groups merged, False if already connected.
`connected(a,b)` and `size(a)` query; unknown items raise KeyError before mutation.
`count` counts components. `snapshot()` returns a nonnegative integer history
position. Each successful union adds ONE position; redundant union adds none.
`rollback(mark)` undoes successful unions after mark, rejecting noninteger marks
(including bool), negative marks and marks beyond current position with ValueError
and no changes. Reusing a position after branching is allowed: marks denote
positions, not immutable versions. `members(a)` returns a frozenset of a's group.
Support at least 1000 items and nested rollbacks. Avoid full state copies per
union: use union by size and a change log; do not compress paths unless undoable.
Construction order decides roots on equal sizes (root from earlier item wins),
but expose `representative(a)` returning that root item to make this deterministic.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
