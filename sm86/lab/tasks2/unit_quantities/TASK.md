# Exact unit quantities and compound input
Extend `parse(text)` returning Fraction bytes. Existing grammar is one decimal
number with a unit. Add a sum of signed terms separated by '+' or '-' (unary sign
allowed only on first term). Each term is a nonnegative decimal with at least
one digit on both sides of an optional decimal point, then optional whitespace,
then case-sensitive unit B/KB/MB/GB (powers 1000) or KiB/MiB/GiB (powers 1024).
Whitespace allowed around terms/operators. Empty, exponent notation, unknown
units, missing units, adjacent terms and repeated signs raise ValueError.
Add `format_bytes(value, unit='B', places=2)` where value is Fraction or int
(bool invalid), unit from same set, places integer 0..6 (bool invalid). Round
exactly half away from zero, fixed point places, append single space and unit;
negative rounded zero displays positive zero. Invalid inputs raise ValueError.
Do not use binary float or ambient Decimal context. Parsing may return negative
or fractional bytes. Existing single-term parsing stays exact.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
