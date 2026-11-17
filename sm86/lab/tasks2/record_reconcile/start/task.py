from copy import deepcopy

def _same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all((_same(a[k], b[k]) for k in a))
    if isinstance(a, list):
        return len(a) == len(b) and all((_same(x, y) for x, y in zip(a, b)))
    return a == b

def _index(records):
    result = {}
    for record in records:
        ident = record.get('id')
        if not isinstance(ident, str) or ident in result:
            raise ValueError('id')
        result[ident] = record
    return result

def reconcile(old, new, renames=None):
    a, b = (_index(old), _index(new))
    if renames:
        raise NotImplementedError('rename mapping')
    renames = {}
    if len(set(renames.values())) != len(renames):
        raise ValueError('targets')
    for src, dst in renames.items():
        if src not in a or dst not in b or (dst in a and dst != src):
            raise ValueError('rename')
    mapped = {renames.get(key, key): value for key, value in a.items()}
    result = [('remove', key) for key in sorted(a) if renames.get(key, key) not in b]
    result += [('rename', src, dst) for src, dst in sorted(renames.items()) if src != dst]
    for ident in sorted(mapped.keys() & b.keys()):
        left, right = (mapped[ident], b[ident])
        changes = {}
        for key in sorted((left.keys() | right.keys()) - {'id'}):
            if key not in right:
                changes[key] = {'$missing': True}
            elif key not in left or not _same(left[key], right[key]):
                changes[key] = deepcopy(right[key])
        if changes:
            result.append(('update', ident, changes))
    result += [('add', deepcopy(b[key])) for key in sorted(b.keys() - mapped.keys())]
    return result
