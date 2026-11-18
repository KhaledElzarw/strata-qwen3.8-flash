from copy import deepcopy
MISSING = object()

def _same(a, b):
    if a is MISSING or b is MISSING:
        return a is b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all((_same(a[k], b[k]) for k in a))
    if isinstance(a, list):
        return len(a) == len(b) and all((_same(x, y) for x, y in zip(a, b)))
    return a == b

def merge(base, left, right):
    conflicts = []

    def clone(value):
        return MISSING if value is MISSING else deepcopy(value)

    def walk(b, l, r, path):
        if _same(l, r):
            return clone(l)
        if _same(l, b):
            return clone(r)
        if _same(r, b):
            return clone(l)
        if isinstance(l, dict) and isinstance(r, dict) and (b is MISSING or isinstance(b, dict)):
            b = {} if b is MISSING else b
            result = {}
            for key in sorted(b.keys() | l.keys() | r.keys()):
                value = walk(b.get(key, MISSING), l.get(key, MISSING), r.get(key, MISSING), path + (key,))
                if value is not MISSING:
                    result[key] = value
            return result
        conflicts.append(path)
        return clone(l)
    result = walk(base, left, right, ())
    return (None if result is MISSING else result, sorted(conflicts))
