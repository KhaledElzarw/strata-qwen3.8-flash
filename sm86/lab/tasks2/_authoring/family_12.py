from common import emit

CLI = '''import io
import json
import subprocess
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from task import main


def run(args, text=''):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(args, io.StringIO(text))
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def external(args, text=''):
    tool = Path(__file__).resolve().parents[1] / 'task.py'
    result = subprocess.run([sys.executable, str(tool), *args], input=text.encode('utf-8'),
                            capture_output=True, timeout=3)
    result.stdout = result.stdout.decode('utf-8').replace(chr(13) + chr(10), chr(10))
    result.stderr = result.stderr.decode('utf-8').replace(chr(13) + chr(10), chr(10))
    return result
'''

emit('json_projection_cli', 'cli', 2, 'implement', '''
# JSON lines projection CLI
Implement task.py, run as `python task.py FIELD [--missing skip|null|error]
[--where KEY=JSON]`. FIELD and KEY are dot-separated nonempty dict keys; empty
segments raise argparse usage error (exit 2). No list traversal. Read UTF-8 JSON
objects one per nonblank stdin line, with physical line numbers including blanks.
--where may repeat and all equality filters apply; compare recursive type-strict
JSON equality, and missing filter keys never match. Malformed KEY=JSON is usage
error 2. Parse/validate every input line even if filtered out. Nonobject or invalid
JSON gives stderr `error: line N` and exit 1. Output selected FIELD as compact
JSON, ensure_ascii=False, one per LF. Missing projected field defaults to skip;
null emits null; error gives same line diagnostic. Buffer ALL output until every
line succeeds: data error prints no stdout. Empty input succeeds. `main(argv=None,
stdin=None)` returns status (argparse may raise SystemExit); import has no effects.
''', '''
import argparse
import json
import sys


def _path(text):
    parts = text.split('.')
    if not all(parts): raise argparse.ArgumentTypeError('empty path')
    return parts


def _filter(text):
    key, sep, value = text.partition('=')
    if not sep: raise argparse.ArgumentTypeError('filter')
    try: return _path(key), json.loads(value)
    except ValueError: raise argparse.ArgumentTypeError('filter') from None


def _same(a, b):
    if type(a) is not type(b): return False
    if isinstance(a, dict): return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list): return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def _get(record, parts, missing):
    for part in parts:
        if not isinstance(record, dict) or part not in record: return missing
        record = record[part]
    return record


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('field', type=_path)
    parser.add_argument('--missing', choices=['skip', 'null', 'error'], default='skip')
    parser.add_argument('--where', type=_filter, action='append', default=[])
    args = parser.parse_args(argv)
    output, missing = [], object()
    for number, line in enumerate(sys.stdin if stdin is None else stdin, 1):
        if not line.strip(): continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict): raise ValueError('object')
            if any(not _same(_get(row, key, missing), value) for key, value in args.where): continue
            value = _get(row, args.field, missing)
            if value is missing:
                if args.missing == 'skip': continue
                if args.missing == 'error': raise ValueError('missing')
                value = None
            output.append(json.dumps(value, ensure_ascii=False, separators=(',', ':')))
        except ValueError:
            print(f'error: line {number}', file=sys.stderr)
            return 1
    for line in output: print(line)
    return 0


if __name__ == '__main__': raise SystemExit(main())
''', [
"assert run(['a'], '{\"a\":1}\\n') == (0, '1\\n', '')",
"assert run(['a', '--missing', 'null'], '{}\\n')[1] == 'null\\n'",
"assert run(['a', '--where', 'b=2'], '{\"a\":1,\"b\":2}\\n{\"a\":3,\"b\":1}')[1] == '1\\n'",
"r = run(['x'], '{\"x\":1}\\n\\nnot-json')\nassert r == (1, '', 'error: line 3\\n')",
"assert run(['a'], '{}')[1] == ''\nassert run(['a', '--missing', 'error'], '{}') == (1, '', 'error: line 1\\n')",
"assert run(['a.b'], '{\"a\":{\"b\":[1,2]}}')[1] == '[1,2]\\n'\nassert run(['a'], '{\"a\":\"é\"}')[1] == '\"é\"\\n'",
"for args in [[], ['a..b'], ['a', '--where', 'bad'], ['a', '--where', 'x=no'], ['a', '--missing', 'bad']]:\n    assert run(args)[0] == 2",
"assert run(['x', '--where', 'v=1'], '{\"x\":3,\"v\":true}')[1] == ''\nassert run(['x', '--where', 'v=null'], '{\"x\":3}')[1] == ''\nassert run(['x'], '[]')[0] == 1",
"r = external(['x'], '{\"x\":2}\\n')\nassert (r.returncode, r.stdout, r.stderr) == (0, '2\\n', '')\nassert run(['x'], '') == (0, '', '')",
], imports=CLI)

emit('group_totals_cli', 'cli', 2, 'fix', '''
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
''', r'''
import argparse
import re
import sys


def _positive(text):
    try: value = int(text)
    except ValueError: raise argparse.ArgumentTypeError('integer') from None
    if value <= 0: raise argparse.ArgumentTypeError('positive')
    return value


def main(argv=None, stdin=None):
    p = argparse.ArgumentParser()
    p.add_argument('--top', type=_positive)
    p.add_argument('--min-total', type=int)
    p.add_argument('--sort', choices=['name', 'total'], default='total')
    a = p.parse_args(argv)
    totals = {}
    for n, line in enumerate(sys.stdin if stdin is None else stdin, 1):
        line = line.rstrip('\n')
        if not line.strip(): continue
        fields = line.split('\t')
        if len(fields) != 2 or not fields[0] or not re.fullmatch(r'-?[0-9]+', fields[1]):
            print(f'error: line {n}', file=sys.stderr)
            return 1
        name, value = fields
        totals[name] = totals.get(name, 0) + int(value)
    rows = [(name, value) for name, value in totals.items() if a.min_total is None or value >= a.min_total]
    rows.sort(key=(lambda r: r[0]) if a.sort == 'name' else (lambda r: (-r[1], r[0])))
    if a.top is not None: rows = rows[:a.top]
    for name, value in rows: print(f'{name}\t{value}')
    return 0


if __name__ == '__main__': raise SystemExit(main())
''', [
"assert run([], 'a\\t2\\na\\t3\\nb\\t1')[1] == 'a\\t5\\nb\\t1\\n'",
"assert run(['--sort', 'name'], 'b\\t5\\na\\t1')[1] == 'a\\t1\\nb\\t5\\n'",
"assert run(['--top', '1'], 'a\\t1\\nb\\t3')[1] == 'b\\t3\\n'",
"assert run([], 'b\\t2\\na\\t2')[1] == 'a\\t2\\nb\\t2\\n'",
"assert run(['--min-total', '3'], 'a\\t2\\na\\t2\\nb\\t5\\nb\\t-3')[1] == 'a\\t4\\n'",
"assert run(['--min-total', '3'], 'a\\t3')[1] == 'a\\t3\\n'\nassert run(['--top', '1', '--min-total', '0'], 'a\\t-1\\nb\\t2')[1] == 'b\\t2\\n'\nassert run([], 'a\\t-2\\nb\\t0')[1] == 'b\\t0\\na\\t-2\\n'",
"for args in [['--top', '0'], ['--top', '-1'], ['--top', 'x'], ['--sort', 'bad'], ['--min-total', 'x']]:\n    assert run(args)[0] == 2",
"for bad in ['bad', 'a\\t1\\t2', '\\t1', 'a\\t 1', 'a\\t+1']:\n    assert run([], 'ok\\t1\\n\\n' + bad) == (1, '', 'error: line 3\\n')",
"r = external([], 'a\\t2\\n')\nassert (r.returncode, r.stdout, r.stderr) == (0, 'a\\t2\\n', '')\nassert run([], '') == (0, '', '')",
], imports=CLI, start=[('task.py', "totals.get(name, 0) + int(value)", 'int(value)'), ('task.py', '(-r[1], r[0])', '(r[1], r[0])'), ('task.py', "value >= a.min_total", 'value > a.min_total')])

emit('ordered_options_cli', 'cli', 3, 'extend', '''
# Ordered configuration operations CLI
Extend task.py, run as `python task.py [--set KEY=JSON] [--unset KEY] [--append
KEY=JSON] [--pretty]`. Stdin is one JSON object (empty/whitespace stdin means {}).
Operations may repeat and MUST apply in original argument order across flags.
KEY is dot-separated segments matching `[A-Za-z_][A-Za-z0-9_]*`. set creates
missing parent dicts and replaces the final value. unset removes existing final
key, ignores missing path, but scalar/list parent is an error. append creates a
missing final list, appends ONE JSON value; nonlist final or nondict parent errors.
Missing parents for append are created like set. set/unset legacy behavior stays.
Argument syntax, invalid KEY/JSON, unknown flags or missing option values give
argparse usage error 2. Invalid/nonobject stdin or applying an operation through
a nondict gives stderr `error: data` and returns 1, no stdout. Output one JSON
object plus LF, keys sorted, ensure_ascii=False; compact separators by default,
indent=2 with --pretty. No operations still normalizes input. Buffer output.
main(argv=None, stdin=None) may raise SystemExit for usage; import has no effects.
''', r'''
import argparse
import json
import re
import sys


class Operation(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        key, sep, value = values.partition('=')
        kind = option_string[2:]
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*', key):
            parser.error('key')
        if kind != 'unset':
            if not sep: parser.error('value')
            try: value = json.loads(value)
            except ValueError: parser.error('json')
        elif sep: parser.error('unset key')
        operations = list(getattr(namespace, 'operations', None) or [])
        operations.append((kind, key.split('.'), value))
        namespace.operations = operations


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser()
    for option in ['set', 'unset', 'append']:
        parser.add_argument('--' + option, action=Operation)
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)
    try:
        text = (sys.stdin if stdin is None else stdin).read()
        data = json.loads(text) if text.strip() else {}
        if not isinstance(data, dict): raise ValueError('object')
        for kind, path, value in getattr(args, 'operations', []):
            parent = data
            missing = False
            for key in path[:-1]:
                if not isinstance(parent, dict): raise ValueError('parent')
                if key not in parent:
                    if kind == 'unset': missing = True; break
                    parent[key] = {}
                parent = parent[key]
            if missing: continue
            if not isinstance(parent, dict): raise ValueError('parent')
            key = path[-1]
            if kind == 'set': parent[key] = value
            elif kind == 'unset': parent.pop(key, None)
            else:
                parent.setdefault(key, [])
                if not isinstance(parent[key], list): raise ValueError('list')
                parent[key].append(value)
    except ValueError:
        print('error: data', file=sys.stderr)
        return 1
    options = {'sort_keys': True, 'ensure_ascii': False}
    if args.pretty: options['indent'] = 2
    else: options['separators'] = (',', ':')
    print(json.dumps(data, **options))
    return 0


if __name__ == '__main__': raise SystemExit(main())
''', [
"assert run(['--set', 'x=1'])[1] == '{\"x\":1}\\n'",
"assert run(['--unset', 'x'], '{\"x\":1}')[1] == '{}\\n'",
"assert run(['--append', 'x=1', '--append', 'x=2'])[1] == '{\"x\":[1,2]}\\n'",
"args = ['--set', 'x=[]', '--append', 'x=1', '--unset', 'x', '--append', 'x=2']\nassert run(args)[1] == '{\"x\":[2]}\\n'",
"assert run(['--append', 'a.b=[1,2]'])[1] == '{\"a\":{\"b\":[[1,2]]}}\\n'\nassert run(['--unset', 'missing.path'])[1] == '{}\\n'",
"for args in [['--set', 'a..b=1'], ['--set', 'x=no'], ['--unset', 'x=1'], ['--append'], ['--bad']]:\n    assert run(args)[0] == 2",
"for args, text in [([], '[]'), ([], 'bad'), (['--set', 'x.y=1'], '{\"x\":2}'), (['--append', 'x=1'], '{\"x\":2}'), (['--unset', 'x.y'], '{\"x\":2}')]:\n    assert run(args, text) == (1, '', 'error: data\\n')",
"assert run(['--pretty'], '{\"b\":2,\"a\":1}')[1] == '{\\n  \"a\": 1,\\n  \"b\": 2\\n}\\n'\nassert run([], '{\"é\":1}')[1] == '{\"é\":1}\\n'",
"r = external(['--set', 'x=3'])\nassert (r.returncode, r.stdout, r.stderr) == (0, '{\"x\":3}\\n', '')\nassert run([], '  ')[1] == '{}\\n'",
], imports=CLI, start=[('task.py', "for option in ['set', 'unset', 'append']:", "for option in ['set', 'unset']:"), ('task.py', "parser.add_argument('--pretty', action='store_true')", "parser.set_defaults(pretty=False)")])

emit('line_selection_cli', 'cli', 3, 'implement', '''
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
prints LF (or 'N:\n'). main(argv=None, stdin=None) returns 0 on valid input;
argparse may raise SystemExit. Import does no I/O. No filesystem/network access.
''', r'''
import argparse
import re
import sys


def _selector(text):
    intervals = []
    number = r'[1-9][0-9]*'
    for term in text.split(','):
        if re.fullmatch(number, term):
            intervals.append((int(term), int(term)))
        elif re.fullmatch(r'(?:' + number + r')?-(?:' + number + r')?', term) and term != '-':
            low, high = term.split('-')
            low = int(low) if low else 1
            high = int(high) if high else None
            if high is not None and low > high: raise argparse.ArgumentTypeError('reversed')
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
        chosen = any(index >= lo and (hi is None or index <= hi) for lo, hi in args.selector)
        if args.invert: chosen = not chosen
        if not chosen: continue
        if args.unique and line in seen: continue
        seen.add(line)
        print(f'{index}:{line}' if args.number else line)
    return 0


if __name__ == '__main__': raise SystemExit(main())
''', [
"assert run(['2-3'], 'a\\nb\\nc\\nd')[1] == 'b\\nc\\n'",
"assert run(['1,3', '--invert'], 'a\\nb\\nc')[1] == 'b\\n'",
"assert run(['1-', '--number'], 'a\\nb')[1] == '1:a\\n2:b\\n'",
"assert run(['3,1-2,2-4'], 'a\\nb\\nc\\nd')[1] == 'a\\nb\\nc\\nd\\n'",
"assert run(['--', '-2'], 'a\\nb\\nc')[1] == 'a\\nb\\n'\nassert run(['5-'], 'a\\nb')[1] == ''",
"assert run(['1-', '--unique', '--number'], 'a\\nb\\na\\nb\\nc')[1] == '1:a\\n2:b\\n5:c\\n'",
"assert run(['1', '--invert', '--unique', '--number'], 'a\\na\\nb\\na')[1] == '2:a\\n3:b\\n'",
"for s in ['', '0', '01', '3-2', '-', '1,,2', ' 1', '1-2-3']:\n    assert run(['--', s])[0] == 2\nassert run(['1'], '') == (0, '', '')",
"r = external(['1-', '--number'], 'a\\r\\n\\r\\nb')\nassert (r.returncode, r.stdout, r.stderr) == (0, '1:a\\n2:\\n3:b\\n', '')\nassert run(['1-'], '\\n')[1] == '\\n'",
], imports=CLI)
