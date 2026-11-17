from copy import deepcopy
import re

def _equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all((_equal(a[k], b[k]) for k in a))
    if isinstance(a, list):
        return len(a) == len(b) and all((_equal(x, y) for x, y in zip(a, b)))
    return a == b

def _parts(path):
    if path == '':
        return []
    if not path.startswith('/') or re.search('~(?![01])', path):
        raise ValueError('pointer')
    return [p.replace('~1', '/').replace('~0', '~') for p in path[1:].split('/')]

def _key(parent, part, add=False):
    if isinstance(parent, dict):
        return part
    if not isinstance(parent, list):
        raise KeyError(part)
    if add and part == '-':
        return len(parent)
    if not re.fullmatch('0|[1-9][0-9]*', part):
        raise ValueError('index')
    index = int(part)
    if index >= len(parent) + int(add):
        raise KeyError(part)
    return index

def apply(document, operations):
    result = deepcopy(document)
    for operation in operations:
        op, path = (operation['op'], _parts(operation['path']))
        if op not in ('add', 'replace', 'remove', 'test'):
            raise ValueError('operation')
        if not path:
            if op == 'test':
                if not _equal(result, operation['value']):
                    raise ValueError('test')
            else:
                result = None if op == 'remove' else deepcopy(operation['value'])
            continue
        parent = result
        for part in path[:-1]:
            parent = parent[_key(parent, part)]
        key = _key(parent, path[-1], op == 'add')
        if op == 'add':
            value = deepcopy(operation['value'])
            if isinstance(parent, list):
                parent.insert(key, value)
            else:
                parent[key] = value
        elif op == 'remove':
            del parent[key]
        elif op == 'replace':
            parent[key]
            parent[key] = deepcopy(operation['value'])
        elif not _equal(parent[key], operation['value']):
            raise ValueError('test')
    return result
