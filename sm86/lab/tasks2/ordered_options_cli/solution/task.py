import argparse
import json
import re
import sys

class Operation(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        key, sep, value = values.partition('=')
        kind = option_string[2:]
        if not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*(?:\\.[A-Za-z_][A-Za-z0-9_]*)*', key):
            parser.error('key')
        if kind != 'unset':
            if not sep:
                parser.error('value')
            try:
                value = json.loads(value)
            except ValueError:
                parser.error('json')
        elif sep:
            parser.error('unset key')
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
        if not isinstance(data, dict):
            raise ValueError('object')
        for kind, path, value in getattr(args, 'operations', []):
            parent = data
            missing = False
            for key in path[:-1]:
                if not isinstance(parent, dict):
                    raise ValueError('parent')
                if key not in parent:
                    if kind == 'unset':
                        missing = True
                        break
                    parent[key] = {}
                parent = parent[key]
            if missing:
                continue
            if not isinstance(parent, dict):
                raise ValueError('parent')
            key = path[-1]
            if kind == 'set':
                parent[key] = value
            elif kind == 'unset':
                parent.pop(key, None)
            else:
                parent.setdefault(key, [])
                if not isinstance(parent[key], list):
                    raise ValueError('list')
                parent[key].append(value)
    except ValueError:
        print('error: data', file=sys.stderr)
        return 1
    options = {'sort_keys': True, 'ensure_ascii': False}
    if args.pretty:
        options['indent'] = 2
    else:
        options['separators'] = (',', ':')
    print(json.dumps(data, **options))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
