# Capped proportional allocation
Implement `allocate(total, weights, caps=None)` returning dict name -> integer
allocation. total is nonnegative integer; weights maps string names to positive
integer weights. caps optionally maps names to nonnegative integer upper bounds;
unspecified caps mean total. Unknown cap keys or insufficient aggregate capacity
raise ValueError; bool/noninteger/invalid total, weight or cap also raise ValueError.
For nonzero total and no names raise ValueError; zero total returns all zeros.
Algorithm: repeatedly compute exact weighted quotas of REMAINING units over
remaining names. Simultaneously fix every name whose quota >= its remaining cap
to that cap, remove them, and recompute. Once no cap binds, floor all quotas then
give the remaining units to largest fractional remainders, ties lexical name.
Use integer/rational arithmetic, never floats. Return all names, including zeros.
Inputs are unchanged and input dictionary insertion order must not affect ties.

Add changes(total, weights, previous, caps=None): return sorted (name, delta)
pairs for nonzero differences from allocate's result. previous maps only known
names to nonnegative integers; missing names mean zero. Reject invalid/unknown
previous entries with ValueError even if total or cap is also invalid. Do not
mutate previous. This reports movement, not a new allocation algorithm.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
