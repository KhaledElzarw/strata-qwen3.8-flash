# Balanced row rounding
Implement `round_rows(rows, places=2)` for a list of rows of finite decimal
strings. Return lists of fixed-point strings. Each row must round as a whole:
round its exact sum half to even to the target number of places. Start each
cell at its floor (toward negative infinity) at that precision; distribute the
remaining quantum units to cells by decreasing fractional remainder, breaking
ties by smaller column index. Consequently each output cell is either its floor
or ceiling, and the output row sum equals its rounded exact sum. Empty rows stay
empty. places is integer 0..6, bool invalid; invalid options or nonfinite/invalid
numbers raise ValueError. Negative zero prints positive. No caller mutation,
no binary floats, and caller Decimal context must not affect results. Tested
inputs have <=30 digits and absolute exponent <=30. Rows round independently.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
