# Strong components with condensation and reachability
Extend `components(graph)` and add `condense(graph)` and `reachable(graph, node)`.
graph maps string nodes to iterable outgoing neighbors; duplicates ignored.
Unknown neighbors or queried node raise KeyError. No input mutation.
components returns strongly connected components as sorted tuples, with the
list sorted lexicographically by tuple. Support >=1200 nodes in a chain without
hitting Python recursion limits. condense returns `(groups, edges)` where groups
is components' result, each component ID its list index, edges sorted unique
`(source_id, target_id)` pairs, excluding within-component edges. reachable
returns sorted nodes reachable by any directed path INCLUDING the starting node.
Validate all graph edges even if unreachable from queried node. Empty graph
returns [] / ([], []). Accept one-shot neighbor iterables for each call.
Keep existing components results on small graphs; remove recursion-depth limits.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
