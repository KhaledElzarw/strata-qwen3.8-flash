import argparse
import re
import sys

def _selector(text):
    intervals = []
    number = '[1-9][0-9]*'
    for term in text.split(','):
        if re.fullmatch(number, term):
            intervals.append((int(term), int(term)))
        elif re.fullmatch('(?:' + number + ')?-(?:' + number + ')?', term) and term != '-':
            low, high = term.split('-')
            low = int(low) if low else 1
            high = int(high) if high else None
            if high is not None and low > high:
                raise argparse.ArgumentTypeError('reversed')
            intervals.append((low, high))
        else:
            raise argparse.ArgumentTypeError('selector')
    return intervals

def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('selector', type=_selector)
    parser.add_argument('--invert', action='store_true')
    parser.add_argument('--number', action='store_true')
    parser.add_argument('--unique', action='store_true')
    args = parser.parse_args(argv)
    seen = set()
    for index, line in enumerate((sys.stdin if stdin is None else stdin).read().splitlines(), 1):
        chosen = any((index >= lo and (hi is None or index <= hi) for lo, hi in args.selector))
        if args.invert:
            chosen = not chosen
        if not chosen:
            continue
        if args.unique and line in seen:
            continue
        seen.add(line)
        print(f'{index}:{line}' if args.number else line)
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
