# Repair grouped integer totals CLI
Fix `python task.py [--top N] [--min-total T] [--sort name|total]`. Stdin has
nonblank lines `NAME<TAB>INTEGER`; name is nonempty and contains no tab, integer
matches -?[0-9]+ with no spaces. Blank lines ignored; physical line numbers count.
Aggregate integer totals by exact case-sensitive name. Default sort is total:
descending total, ties lexical name; name sort is lexical. min-total is an integer
threshold applied AFTER aggregation. top is positive integer, else usage error
2; apply it AFTER threshold and sorting. Print `NAME<TAB>TOTAL` with LF per row.
Bad data prints `error: line N` on stderr and returns 1 with NO stdout, even if
previous lines were valid. All argument errors exit 2. Empty input succeeds.
main(argv=None, stdin=None) may raise argparse SystemExit. Import does no I/O.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
