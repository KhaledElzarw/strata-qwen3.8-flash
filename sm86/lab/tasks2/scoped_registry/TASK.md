# Scoped command registry with compatibility wrappers
Refactor `register`, `invoke`, `names` module functions to delegate to
`default_registry` of new class `Registry(parent=None)`. A registry owns local
commands and aliases; parent is another Registry or None. `register(name, fn)`
requires nonempty string name, callable fn, and no LOCAL name collision (including
aliases), else ValueError. `alias(name, target)` requires nonempty string names
and no local collision, but may refer to missing/future targets. Child definitions
shadow inherited names. `invoke(name, *args, **kwargs)` resolves aliases from the
ORIGINAL invoking registry, even when alias itself was inherited; missing name
raises KeyError and any alias cycle raises ValueError. Call fn with exactly the
supplied args/kwargs, propagating exceptions and returning its result. `names()`
returns sorted union of local and inherited names including unresolved aliases.
`unregister(name)` removes only local entries, returning bool; an inherited
entry may become visible again. Add module alias/unregister wrappers too.
Parent state never changes through child mutation. Existing function invocation
behavior must remain, and separate root registries never share state.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
