# Maximum matching with cost and lexical ties
Implement `match(costs)` where costs maps worker string -> dict job string ->
integer cost; absent edges are forbidden. Each worker/job can be used at most
once. Return `(pairs, total_cost)` with pairs a sorted tuple of `(worker, job)`.
First maximize the number of pairs, then minimize total cost (negative costs
allowed), then choose the lexicographically smallest pairs tuple. Empty/isolated
workers are valid. Reject bool or noninteger costs with ValueError. Do not mutate
inputs. Handle up to 12 distinct jobs and 20 workers; enumerating all matchings
is too slow. Use subset dynamic programming or a polynomial matching algorithm.
Job IDs come from all inner keys; workers may remain unmatched. Empty input
returns `((), 0)`. Ties compare the whole sorted pairs sequence, not just jobs.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
