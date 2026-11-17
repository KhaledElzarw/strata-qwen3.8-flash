# Invoice calculation bug hunt
Repair the three-module invoice calculator `invoice(lines, discount='0', tax='0')`.
Each line is dict with sku string, quantity positive integer (bool invalid),
and price a nonnegative finite Decimal-compatible string. discount and tax are
finite decimal strings: 0 <= discount <= 1 and tax >= 0. Invalid values raise
ValueError. Compute each extended price quantity*price, apply (1-discount), then
round EACH discounted line to cents with ROUND_HALF_UP. Subtotal is sum of these
rounded lines. Tax is subtotal*tax rounded once HALF_UP to cents. Return dict
`lines` (list `(sku, formatted_line_total)` in input order), `subtotal`, `tax`,
`total`, all money strings with exactly two fractional digits; total=subtotal+tax.
Use Decimal throughout, independent of caller Decimal precision/rounding context;
values tested have at most 30 significant digits. No input mutation; empty lines
are valid and still validate rates. Keep task.py, money.py and pricing.py API.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
