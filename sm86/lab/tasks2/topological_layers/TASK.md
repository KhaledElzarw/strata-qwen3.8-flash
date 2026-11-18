# Repair dependency layers and blocked nodes
Fix `layers(graph)` for dict node -> iterable of prerequisite string nodes.
Prerequisites must exist, else KeyError. Duplicates count once; inputs unchanged.
Return `(rounds, blocked)`: rounds is a list of sorted lists. In each round emit
ALL nodes whose prerequisites were completed in EARLIER rounds, never same round.
Continue until none are ready. blocked is sorted nodes left, including both
cycle members and acyclic nodes depending on a cycle. Empty graph gives ([], []).
A self dependency blocks itself. Distinct insertion orders yield identical
results. Handle disconnected graphs and at least 500 nodes. Do not raise for
cycles. Implement `order(graph)` flattening rounds; if any blocked nodes exist,
raise ValueError whose only argument is tuple(blocked), with no partial order.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
