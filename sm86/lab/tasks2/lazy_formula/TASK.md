# Lazy formula evaluation
Extend `evaluate(node, env)` in `task.py`. Nodes are integers, strings (variable
names), or tuples `(operator, ...)`. Existing eager binary add/sub/mul/eq/lt
return integers (comparisons return 0 or 1). Add lazy `if(cond, yes, no)`,
`and(left, right)`, `or(left, right)`, and `let(name, value, body)`. For and/or,
return 0 or 1 using integer truth; skip the right branch when determined.
For if evaluate only the chosen branch. let evaluates value in the outer scope,
then body with a shadowing local binding; outer env must stay unchanged.
Missing names raise KeyError. Unknown operators, wrong arities, noninteger
nonstring nontuple nodes and nonstring let names raise ValueError when visited.
Booleans are invalid nodes even though Python treats them as ints. Validation
is lazy too: unreachable invalid nodes or missing names must not fail. Tuples
must be nonempty with a string operator. No mutation of nodes or env.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
