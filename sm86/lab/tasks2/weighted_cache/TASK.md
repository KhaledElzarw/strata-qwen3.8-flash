# Weight-bounded cache
Implement `Cache(budget, clock)` with positive integer budget, else ValueError.
`put(key, value, weight=1, ttl=None)` requires positive weight and ttl None or
nonnegative; invalid arguments raise ValueError before altering anything. Purge
all expired entries first. Replace an existing key, then evict least recently
used entries until total weight <= budget. An oversized entry is not stored,
but DOES remove an older value of the same key. ttl=0 expires immediately;
expiry is now >= insertion_time + ttl. get(key, default=None) purges expiry and
makes a hit most recent without extending ttl. contains via `key in cache`
purges but does not affect recency. `keys()` returns live keys least to most
recent; `weight` returns live total weight. Read time once per public operation.
Values are stored by reference; instances are independent. clock is injected.

Add resize(budget): validate positive budget before mutation, purge once at the
injected current time, set budget, and evict LRU entries until weight fits.
Growing preserves recency and expiry. Read clock once; invalid resize does not.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
