# Deterministic shortest routes
Implement `route(graph, start, goal)`. graph maps string nodes to lists of
`(neighbor, weight)` directed edges; every neighbor must be a graph key, else
KeyError. All weights must be nonnegative integers (bool invalid), else ValueError.
Validate ALL edges, including unreachable ones. Missing start/goal raises
KeyError. Return `(cost, path)` with path a tuple including both endpoints, or
None when unreachable. Minimize cost, then number of edges, then full path
lexicographically. Parallel edges and self loops are allowed. start==goal returns
(0,(start,)) after validation. Do not mutate graph. Support at least 300 nodes;
use a shortest-path algorithm, not enumeration of all paths. Zero-cost cycles
must terminate and never improve an equal-cost route with extra hops.

Add routes(graph, start): return dict reachable node -> (cost, path), including
start, under exactly the same ties and validation. Compute all routes with one
shortest-path search, not repeated route calls.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
