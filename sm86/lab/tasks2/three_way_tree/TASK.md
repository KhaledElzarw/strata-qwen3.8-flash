# Three-way tree merge
Implement `merge(base, left, right)` returning `(merged, conflicts)`. JSON-like
values have string dict keys. Equality is recursive and type-strict. At any path,
if left == right take it; if left == base take right; if right == base take left.
Otherwise, when all PRESENT values at that path are dicts (at least left and
right must be present dicts), recursively merge their union of keys; an absent
base is treated as {}. Absence is distinct from None. All other concurrent
changes conflict: keep LEFT including its deletion. Record that path as a tuple
of dict keys, root as (). Lists are atomic, never merged element by element.
Missing keys on both sides disappear. Conflicts are sorted lexicographically;
record only the conflicting parent if recursion is not allowed, not descendants.
Return deeply independent values, never mutate inputs. Delete versus unchanged
is a deletion; delete versus modified is a conflict. If merged root were absent
it would be None, though all three supplied roots are always present.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
