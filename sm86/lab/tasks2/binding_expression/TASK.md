# Integer expressions with bindings
Implement `evaluate(text, variables=None)`. Grammar has ASCII nonnegative integer
literals, identifiers `[A-Za-z_][A-Za-z0-9_]*`, parentheses, binary + - * // %,
and unary + -. Whitespace is ignored between tokens, never inside a token.
Unary signs bind tighter than multiplication; multiplication, floor division and
modulo bind tighter than addition/subtraction. Binary operators associate left.
Variables maps identifiers to integers; missing names raise KeyError. Python
integer // and % rules apply, including negative operands; zero divisors raise
ZeroDivisionError. Reject empty input, unknown characters, adjacent operands,
unmatched parentheses and trailing tokens with ValueError. Consume all input;
do not use eval or exec. Do not modify variables.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
