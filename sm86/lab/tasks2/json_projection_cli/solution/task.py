import argparse
import json
import sys

def _path(text):
    parts = text.split('.')
    if not all(parts):
        raise argparse.ArgumentTypeError('empty path')
    return parts

def _filter(text):
    key, sep, value = text.partition('=')
    if not sep:
        raise argparse.ArgumentTypeError('filter')
    try:
        return (_path(key), json.loads(value))
    except ValueError:
        raise argparse.ArgumentTypeError('filter') from None

def _same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all((_same(a[k], b[k]) for k in a))
    if isinstance(a, list):
        return len(a) == len(b) and all((_same(x, y) for x, y in zip(a, b)))
    return a == b

def _get(record, parts, missing):
    for part in parts:
        if not isinstance(record, dict) or part not in record:
            return missing
        record = record[part]
    return record

def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('field', type=_path)
    parser.add_argument('--missing', choices=['skip', 'null', 'error'], default='skip')
    parser.add_argument('--where', type=_filter, action='append', default=[])
    args = parser.parse_args(argv)
    output, missing = ([], object())
    for number, line in enumerate(sys.stdin if stdin is None else stdin, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError('object')
            if any((not _same(_get(row, key, missing), value) for key, value in args.where)):
                continue
            value = _get(row, args.field, missing)
            if value is missing:
                if args.missing == 'skip':
                    continue
                if args.missing == 'error':
                    raise ValueError('missing')
                value = None
            output.append(json.dumps(value, ensure_ascii=False, separators=(',', ':')))
        except ValueError:
            print(f'error: line {number}', file=sys.stderr)
            return 1
    for line in output:
        print(line)
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
