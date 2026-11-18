"""Layered object overlays with deletion and change histories.

Deletion markers are exact and type-sensitive.
List contents are data rather than overlay instructions."""
from copy import deepcopy

def _delete(value):
    return isinstance(value, dict) and set(value) == {'$delete'} and (value['$delete'] == True)

def _overlay(base, layer):
    result = deepcopy(base)
    for key, value in layer.items():
        if _delete(value):
            result.pop(key, None)
        elif isinstance(value, dict):
            old = result.get(key)
            result[key] = _overlay(old if isinstance(old, dict) else {}, value)
        else:
            result[key] = value
    return result

def merge(base, layers):
    if not isinstance(base, dict):
        raise ValueError('base')
    result = deepcopy(base)
    for layer in layers:
        if not isinstance(layer, dict):
            raise ValueError('layer')
        result = _overlay(result, layer)
    return result

def _same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all((_same(a[k], b[k]) for k in a))
    if isinstance(a, list):
        return len(a) == len(b) and all((_same(x, y) for x, y in zip(a, b)))
    return a == b

def _changes(before, after, prefix=()):
    if isinstance(before, dict) and isinstance(after, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            path = prefix + (key,)
            if key not in before or key not in after:
                result.append(path)
            else:
                result.extend(_changes(before[key], after[key], path))
        return result
    return [] if _same(before, after) else [prefix]

def explain(base, layers):
    current = merge(base, [])
    history = []
    for layer in layers:
        updated = merge(current, [layer])
        history.append(_changes(current, updated))
        current = updated
    return (current, history)
