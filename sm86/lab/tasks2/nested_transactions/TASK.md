# Repair nested key transactions
Fix `Store(initial=None)` in `task.py`. Initial is a dict copied deeply. `begin()`
opens a nested transaction; `commit()` keeps changes and closes ONLY the innermost
transaction, and `rollback()` restores the innermost begin snapshot. Either
closing method with no transaction raises ValueError. `set(key, value)` deep
copies its value; `get(key)` returns a deep copy, raising KeyError when missing.
`delete(key)` removes a key or raises KeyError. `snapshot()` is a deep copy of
current contents; `depth` is the count of open transactions. Rolling back an
outer transaction also undoes inner commits. Operations outside transactions
work immediately. Instances, snapshots and supplied mutable values are isolated.

Add transaction() as a context manager yielding this Store: begin on entry,
commit on normal exit, rollback on any BaseException and re-raise it. Contexts
may nest, but their bodies do not manually begin/commit/rollback transactions.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
