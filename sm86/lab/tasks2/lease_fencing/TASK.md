# Lease fencing and atomic writes
Implement `Coordinator(clock)` in task.py using helper modules if useful. clock
is an injected nondecreasing callable returning integer time; never use real time.
`acquire(resource, owner, ttl)` requires ttl > 0 (ValueError otherwise). A live
lease held by another owner returns None. Same owner acquisition renews expiry
from now and keeps its token. An absent or expired lease gets a globally
increasing positive integer token; tokens are never reused across resources.
A lease is expired at now >= expires. `renew(resource, owner, token, ttl)` returns
True only on matching live lease, setting expiry to now + ttl. Invalid ttl always
raises ValueError. `release(resource, owner, token)` returns True only for a
matching live lease and removes it. `write(resource, token, value)` returns True
only if token equals that resource's live lease token; store a deep copy.
`read(resource, default=None)` returns a deep copy of last written value, surviving
release and expiry; default is returned as given when no value exists.
`write_many(items)` takes iterable `(resource, token, value)`; validate all leases
at ONE clock reading, then deep-copy and commit all writes atomically. Duplicate
resources raise ValueError before any write; any stale token returns False with
no writes. Empty batch succeeds. Individual instances share nothing.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
