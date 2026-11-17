# Rolling quota with reservations
Extend `Quota(capacity, window, clock)`. capacity and window must be positive,
else ValueError. Committed requests are retained in the rolling interval
(now-window, now], so expiry at exactly window is removed. Add reservations:
`reserve(key, amount=1, ttl=None)` returns True if total live amount + amount <=
capacity. amount positive, ttl None or positive; invalid arguments or a repeated
LIVE key raise ValueError, before changing live usage. A reservation expires at
ttl if supplied, otherwise after window; ttl may exceed window. `commit(key)`
turns a live reservation into committed usage timestamped NOW, returning True;
missing/expired/already committed key returns False. Committed records keep key
occupied until window expiry. `cancel(key)` removes only live reservations,
returning bool. `used` counts committed and reserved amounts. Purge expiry before
operations and read clock once per call. Existing `take(amount=1)` atomically
adds anonymous committed usage if it fits; False otherwise. Never spend on
failed calls. clock is injected and nondecreasing.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
