# Dependency worker schedule
Implement `schedule(jobs, workers)` returning sorted `(id, worker, start, end)`
tuples in `(start, worker, id)` order. jobs maps string IDs to `(duration, deps)`;
duration is a positive integer, deps an iterable of IDs (duplicates ignored).
workers is positive, else ValueError. Unknown dependencies raise KeyError; any
cycle raises ValueError, even in disconnected components. Do not mutate inputs.
Time begins at zero; all jobs finishing at time t release dependencies BEFORE
new starts at t. Whenever workers are free, assign ready jobs in lexical ID
order to the smallest free worker IDs (0 through workers-1). Running jobs are
never interrupted. Advance time to the next completion when no further start is
possible. Return [] for empty jobs. Validate all input before scheduling. Handle
at least 200 jobs without enumerating possible schedules. No actual clocks.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
