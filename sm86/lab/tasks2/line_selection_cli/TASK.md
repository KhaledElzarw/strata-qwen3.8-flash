# Line selection CLI
Implement task.py: `python task.py SELECTOR [--invert] [--number] [--unique]`.
SELECTOR is comma-separated positive integer positions/ranges: N, A-B, A- or -B.
Use canonical decimals without leading zeros. Ranges inclusive; A>B invalid.
No spaces, empty terms or bare '-' allowed; syntax errors are usage exit 2.
Read all stdin logical lines with str.splitlines(); empty input has zero lines.
Select the UNION in original file order, ignoring positions beyond EOF. --invert
selects the complement. --unique removes repeated selected line TEXT keeping
its first selected occurrence; do it after inversion. --number prefixes original
1-based line number plus ':'; never renumber after filtering. Print each selected
line with LF, including an unterminated input final line. Empty selected line
prints LF (or 'N:
'). main(argv=None, stdin=None) returns 0 on valid input;
argparse may raise SystemExit. Import does no I/O. No filesystem/network access.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
