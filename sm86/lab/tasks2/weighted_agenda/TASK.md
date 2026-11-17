# Weighted agenda with deterministic ties
Implement `select(jobs, gap=0)`. A job is `(id, start, end, reward)`: distinct
string ID, integer times and integer reward. Reject duplicate IDs, start >= end,
or negative gap with ValueError before selecting. Accept any iterable; do not
mutate it. A chosen chronological sequence is compatible when each next start
is at least previous end + gap. Return `(total_reward, ids)` where ids is a tuple
in chronological `(start, end, id)` order. Maximize reward; on ties minimize the
number of jobs; then choose the lexicographically smallest chronological ID
tuple. Empty selection `(0, ())` is allowed. Negative and zero rewards may be
present. Handle at least 300 jobs without enumerating subsets. IDs are compared
as Python strings. Gap applies only between jobs, never at the outer boundaries.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
