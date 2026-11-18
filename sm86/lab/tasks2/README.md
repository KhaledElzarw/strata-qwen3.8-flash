# Harder coding tasks, batch 1

34 independent Python 3.11 tasks in 12 families and three levels (the first batch had 48; 14 were removed after a
review found their starting code already held the solution).
Levels describe intended complexity, not measured model solve rates. Calibrate by
running each task several times and retain tasks solved in 20–80% of runs. This
suite alone does not establish a model quality change or a gain per 100 tasks.

## Agent input

Give an agent only a fresh copy of a task's `start/` plus its `TASK.md` at the
working folder root. Neither `hidden/`, `solution/`, nor other tasks
belong in that folder. There are no Hermes, Claude Code, or other harness APIs.
Python 3.11 and pytest must already be available. Solutions use the standard
library only. Visible tests cover three or four groups; hidden tests include
those groups and at least six more. No network, real clock, or random input is needed.

## Scoring contract

Copy the agent's working folder into a fresh temporary folder. Remove its entire
`tests/` directory and replace it with the task's `hidden/` contents, placed at
`tests/`. From the copied folder run **`python -m pytest -q`**, using the task's
`meta.json` `timeout_s` as a wall time limit for the whole command. Pass means
exit code 0 before that limit; every other exit or a timeout is a failure.
Never overlay the reference solution when scoring an agent.

Use a clean environment with third-party pytest plugin autoload disabled, no
inherited `PYTHONPATH` or `PYTEST_ADDOPTS`, and no parent pytest configuration.
The validator does this in a system temporary folder. The scoring contract is
for cooperative agents; it is not a sandbox against malicious submissions.

## Fairness check

From the repository root run:

```sh
python sm86/lab/tasks2/validate.py
```

For each task the validator checks metadata and layout, requires an executed
hidden test failure on the starting code (collection errors do not qualify),
then requires all hidden tests and visible tests to pass after applying the
reference overlay. Each of these runs has a timeout below ten seconds. The last
line must be `ALL <N> TASKS FAIR`; exit code 0 means all checks passed. For `implement` and `extend` tasks it also
counts the solution lines that are not already in `start/` and fails a task with fewer than 12 (a leak check).
This is a mechanical fairness proof, not a proof that tests cover every possible
implementation error. Specifications are the source of required behavior.

The local conftest.py excludes task fixtures from repository-wide pytest
discovery. It is not copied for scoring.

## Task inventory

| Task | Family | Level | Kind |
| --- | --- | ---: | --- |
| [dependency_hunt](dependency_hunt/TASK.md) | bug_hunts | 4 | fix |
| [inventory_hunt](inventory_hunt/TASK.md) | bug_hunts | 4 | fix |
| [invoice_hunt](invoice_hunt/TASK.md) | bug_hunts | 4 | fix |
| [search_index_hunt](search_index_hunt/TASK.md) | bug_hunts | 4 | fix |
| [group_totals_cli](group_totals_cli/TASK.md) | cli | 2 | fix |
| [json_projection_cli](json_projection_cli/TASK.md) | cli | 2 | implement |
| [line_selection_cli](line_selection_cli/TASK.md) | cli | 3 | implement |
| [binding_expression](binding_expression/TASK.md) | expressions | 2 | implement |
| [postfix_machine](postfix_machine/TASK.md) | expressions | 3 | fix |
| [template_blocks](template_blocks/TASK.md) | expressions | 4 | implement |
| [assignment_matching](assignment_matching/TASK.md) | graphs | 4 | implement |
| [ranked_routes](ranked_routes/TASK.md) | graphs | 2 | implement |
| [topological_layers](topological_layers/TASK.md) | graphs | 3 | fix |
| [coverage_bands](coverage_bands/TASK.md) | intervals | 2 | implement |
| [weighted_agenda](weighted_agenda/TASK.md) | intervals | 4 | implement |
| [balanced_rounding](balanced_rounding/TASK.md) | numeric | 3 | implement |
| [bounded_apportion](bounded_apportion/TASK.md) | numeric | 2 | implement |
| [decimal_display](decimal_display/TASK.md) | numeric | 2 | fix |
| [folded_records](folded_records/TASK.md) | parsers | 3 | fix |
| [header_parameters](header_parameters/TASK.md) | parsers | 2 | implement |
| [include_config](include_config/TASK.md) | parsers | 4 | implement |
| [escaped_frames](escaped_frames/TASK.md) | protocols | 2 | implement |
| [lease_fencing](lease_fencing/TASK.md) | protocols | 4 | implement |
| [event_dispatch](event_dispatch/TASK.md) | refactors | 2 | extend |
| [path_policy](path_policy/TASK.md) | refactors | 3 | fix |
| [atomic_pointer_patch](atomic_pointer_patch/TASK.md) | structured_changes | 2 | implement |
| [overlay_delete](overlay_delete/TASK.md) | structured_changes | 2 | fix |
| [three_way_tree](three_way_tree/TASK.md) | structured_changes | 4 | implement |
| [indexed_priority](indexed_priority/TASK.md) | structures | 3 | fix |
| [prefix_catalog](prefix_catalog/TASK.md) | structures | 2 | implement |
| [rollback_groups](rollback_groups/TASK.md) | structures | 4 | implement |
| [deadline_queue](deadline_queue/TASK.md) | timed_state | 3 | fix |
| [weighted_cache](weighted_cache/TASK.md) | timed_state | 2 | implement |
| [worker_schedule](worker_schedule/TASK.md) | timed_state | 4 | implement |
