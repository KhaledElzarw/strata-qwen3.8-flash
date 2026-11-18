# Repair the transactional postfix machine
Fix `Machine` with `stack` (list of integers) and `variables` (dict). `run(tokens)`
accepts an iterable of strings and returns a fresh copy of the final stack.
Integer tokens match `-?[0-9]+`; `+ - * /` pop right then left (/ truncates toward
zero without float conversion). `dup` duplicates the top; `swap` swaps top two;
`drop` removes top. `$name` pushes a variable and `=name` pops into a variable;
name matches `[A-Za-z_][A-Za-z0-9_]*`. Missing variables raise KeyError. Stack
underflow or bad tokens raise ValueError; zero divisor raises ZeroDivisionError.
A failed run rolls back BOTH stack and variables to their pre-call contents.
Success commits them, and independent Machine instances share nothing. Inputs
are never modified. No arithmetic size limit is imposed on Python integers.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
