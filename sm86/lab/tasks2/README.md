# Harder coding tasks, batch 1

48 independent Python 3.11 tasks, in 12 families of four, with 16 tasks per level.
Levels describe intended complexity, not measured model solve rates. Calibrate by
running each task several times and retain tasks solved in 20–80% of runs. This
suite alone does not establish a model quality change or a gain per 100 tasks.

## Agent input

Give an agent only a fresh copy of a task's `start/` plus its `TASK.md` at the
working folder root. Neither `hidden/`, `solution/`, `_authoring/`, nor other tasks
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
line must be `ALL 48 TASKS FAIR`; exit code 0 means all checks passed.
This is a mechanical fairness proof, not a proof that tests cover every possible
implementation error. Specifications are the source of required behavior.

`_authoring/` contains private, reproducible source material. To regenerate the
task files with the existing Python, run `python sm86/lab/tasks2/_authoring/common.py`.
The authoring helpers never fetch data or install packages.

The local conftest.py excludes task fixtures from repository-wide pytest
discovery. It is not copied for scoring. The validator's own regression tests
live under _authoring/test_validate.py.

## Task inventory

| Family | Level 2 | Level 3 | Level 4 | Implement / fix / extend |
| --- | ---: | ---: | ---: | --- |
| bug_hunts | 0 | 0 | 4 | 0 / 4 / 0 |
| cli | 2 | 2 | 0 | 2 / 1 / 1 |
| expressions | 1 | 1 | 2 | 2 / 1 / 1 |
| graphs | 1 | 1 | 2 | 2 / 1 / 1 |
| intervals | 2 | 1 | 1 | 2 / 1 / 1 |
| numeric | 2 | 2 | 0 | 2 / 1 / 1 |
| parsers | 1 | 2 | 1 | 2 / 1 / 1 |
| protocols | 2 | 1 | 1 | 2 / 1 / 1 |
| refactors | 1 | 2 | 1 | 0 / 1 / 3 |
| structured_changes | 2 | 1 | 1 | 2 / 1 / 1 |
| structures | 1 | 1 | 2 | 2 / 1 / 1 |
| timed_state | 1 | 2 | 1 | 2 / 1 / 1 |

Task IDs and specifications:

- bug_hunts: [dependency_hunt](dependency_hunt/TASK.md), [inventory_hunt](inventory_hunt/TASK.md), [invoice_hunt](invoice_hunt/TASK.md), [search_index_hunt](search_index_hunt/TASK.md)
- cli: [group_totals_cli](group_totals_cli/TASK.md), [json_projection_cli](json_projection_cli/TASK.md), [line_selection_cli](line_selection_cli/TASK.md), [ordered_options_cli](ordered_options_cli/TASK.md)
- expressions: [binding_expression](binding_expression/TASK.md), [lazy_formula](lazy_formula/TASK.md), [postfix_machine](postfix_machine/TASK.md), [template_blocks](template_blocks/TASK.md)
- graphs: [assignment_matching](assignment_matching/TASK.md), [component_condensation](component_condensation/TASK.md), [ranked_routes](ranked_routes/TASK.md), [topological_layers](topological_layers/TASK.md)
- intervals: [coverage_bands](coverage_bands/TASK.md), [room_assignment](room_assignment/TASK.md), [weighted_agenda](weighted_agenda/TASK.md), [working_minutes](working_minutes/TASK.md)
- numeric: [balanced_rounding](balanced_rounding/TASK.md), [bounded_apportion](bounded_apportion/TASK.md), [decimal_display](decimal_display/TASK.md), [unit_quantities](unit_quantities/TASK.md)
- parsers: [delimited_stream](delimited_stream/TASK.md), [folded_records](folded_records/TASK.md), [header_parameters](header_parameters/TASK.md), [include_config](include_config/TASK.md)
- protocols: [escaped_frames](escaped_frames/TASK.md), [lease_fencing](lease_fencing/TASK.md), [nested_transactions](nested_transactions/TASK.md), [ordered_receiver](ordered_receiver/TASK.md)
- refactors: [event_dispatch](event_dispatch/TASK.md), [path_policy](path_policy/TASK.md), [row_codec](row_codec/TASK.md), [scoped_registry](scoped_registry/TASK.md)
- structured_changes: [atomic_pointer_patch](atomic_pointer_patch/TASK.md), [overlay_delete](overlay_delete/TASK.md), [record_reconcile](record_reconcile/TASK.md), [three_way_tree](three_way_tree/TASK.md)
- structures: [indexed_priority](indexed_priority/TASK.md), [prefix_catalog](prefix_catalog/TASK.md), [range_paint](range_paint/TASK.md), [rollback_groups](rollback_groups/TASK.md)
- timed_state: [deadline_queue](deadline_queue/TASK.md), [rolling_quota](rolling_quota/TASK.md), [weighted_cache](weighted_cache/TASK.md), [worker_schedule](worker_schedule/TASK.md)
