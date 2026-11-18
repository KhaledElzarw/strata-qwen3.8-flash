# Repair decimal display rules
Fix `format_number(text, places=2, mode='even', grouping=False)` for finite
Decimal-compatible strings. places is an integer 0..12, bool invalid; mode is
'even' (half to even), 'away' (half away from zero), or 'zero' (truncate toward
zero). Invalid values raise ValueError. Round exactly using Decimal independent
of caller precision/rounding; tested inputs have <= 50 significant digits and
absolute exponent <= 100. Always print fixed point with exactly places digits.
Normalize any rounded negative zero to positive zero. grouping inserts commas
every three INTEGER digits only. No leading '+'; preserve negative sign for
nonzero results. `parse_display(text)` accepts only this grouped or ungrouped
fixed-point output syntax: optional '-', integer 0 or nonzero-leading digits,
optional '.' with one or more digits; grouped integer must have first group
1..3 digits with no leading zero then groups of exactly three. Reject commas
in fractional part, spaces, exponent form, plus signs and negative zero.
Return Decimal; parse_display also works on unrounded fixed point strings.

Add format_column(values, places=2, mode='even', grouping=False): apply
format_number to each value, then left-pad with spaces to the widest formatted
value's length. Return list of strings; [] for no values, but still validate
places/mode. Accept an iterable once. Never strip sign or grouping punctuation.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
