# Event dispatcher with isolated instances
Extend the legacy `subscribe(topic, callback)`, `unsubscribe(topic, callback)`
and `emit(topic, value)` functions by adding `Bus` with the same methods, plus
`default_bus` used by all module wrappers. Subscribe returns True for a new
callback, False if already subscribed to that topic (identity comparison).
Unsubscribe returns bool. Emit returns callback results in subscription order;
callback exceptions propagate and stop dispatch. Dispatch uses a SNAPSHOT of
subscriptions: changes by callbacks affect the next emit, not the current one.
Add `once(topic, callback)` to Bus and module: one-shot subscriptions are removed
BEFORE invoking so recursive emit cannot invoke them twice. Re-subscribing an
already registered callback (once or normal) returns False without changing
its existing mode or order. Each Bus owns independent state. Topics are strings.

Add clear(topic=None): remove all handlers of that topic, or all topics for
None, returning count removed. Dispatch already in progress keeps its snapshot.
Add subscribers(topic): fresh list of callbacks in subscription order. Both
methods belong to Bus and have module wrappers through default_bus.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
