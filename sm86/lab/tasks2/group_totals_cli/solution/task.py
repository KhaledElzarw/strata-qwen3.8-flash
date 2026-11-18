"""Aggregate tab-separated totals before producing output.

Data failures leave standard output empty.
Argument parsing and data validation have separate statuses."""
import argparse
import re
import sys

def _positive(text):
    """Parse a strictly positive command option.

Raise an argparse type error for invalid values.
This keeps usage failures at exit status two."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError('integer') from None
    if value <= 0:
        raise argparse.ArgumentTypeError('positive')
    return value

def main(argv=None, stdin=None):
    """Validate all records, then filter, sort, and limit.

Thresholds apply to totals rather than individual lines.
Output begins only after the full input is accepted."""
    p = argparse.ArgumentParser()
    p.add_argument('--top', type=_positive)
    p.add_argument('--min-total', type=int)
    p.add_argument('--sort', choices=['name', 'total'], default='total')
    a = p.parse_args(argv)
    try:
        totals = _read_totals(sys.stdin if stdin is None else stdin)
    except ValueError as exc:
        print(f'error: line {exc.args[0]}', file=sys.stderr)
        return 1
    rows = [(name, value) for name, value in totals.items() if a.min_total is None or value >= a.min_total]
    rows.sort(key=(lambda r: r[0]) if a.sort == 'name' else lambda r: (-r[1], r[0]))
    if a.top is not None:
        rows = rows[:a.top]
    for name, value in rows:
        print(f'{name}\t{value}')
    return 0

def _read_totals(stream):
    """Read physical lines into exact integer totals.

Blank lines still count toward diagnostic positions.
Raise the failing position without printing partial results."""
    totals = {}
    for n, line in enumerate(stream, 1):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        fields = line.split('\t')
        if len(fields) != 2 or not fields[0] or (not re.fullmatch('-?[0-9]+', fields[1])):
            raise ValueError(n)
        name, value = fields
        totals[name] = totals.get(name, 0) + int(value)
    return totals
if __name__ == '__main__':
    raise SystemExit(main())
