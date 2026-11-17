from common import emit

emit('atomic_pointer_patch', 'structured_changes', 2, 'implement', '''
# Atomic pointer patch
Implement `apply(document, operations)` returning a deep-copied patched value;
never mutate document or operation values. Operations are dicts with `op`, `path`
and (for add/replace/test) `value`; remove needs no value. Paths are '' for root
or slash-separated JSON Pointer segments: ~0 decodes ~ and ~1 decodes /; any
other ~ escape raises ValueError. Dict keys are strings. List segments must be
canonical nonnegative decimal indexes (0 or nonzero digit followed by digits).
For add only, '-' appends and indexes through len(list) insert. Replace/remove/
test require existing items, raising KeyError for missing key or out-of-range
index. Traversing a scalar raises KeyError. Invalid paths/index syntax or unknown
ops raise ValueError. Root add/replace replaces document; root remove produces
None. test checks recursive type-strict equality (True differs from 1), raising
ValueError on mismatch. Apply operations sequentially; an error exposes no partial
mutation to caller. Extra operation fields are ignored. Inputs are JSON-like.
''', r'''
from copy import deepcopy
import re


def _equal(a, b):
    if type(a) is not type(b): return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
    return a == b


def _parts(path):
    if path == '': return []
    if not path.startswith('/') or re.search(r'~(?![01])', path):
        raise ValueError('pointer')
    return [p.replace('~1', '/').replace('~0', '~') for p in path[1:].split('/')]


def _key(parent, part, add=False):
    if isinstance(parent, dict): return part
    if not isinstance(parent, list): raise KeyError(part)
    if add and part == '-': return len(parent)
    if not re.fullmatch(r'0|[1-9][0-9]*', part): raise ValueError('index')
    index = int(part)
    if index >= len(parent) + int(add): raise KeyError(part)
    return index


def apply(document, operations):
    result = deepcopy(document)
    for operation in operations:
        op, path = operation['op'], _parts(operation['path'])
        if op not in ('add', 'replace', 'remove', 'test'): raise ValueError('operation')
        if not path:
            if op == 'test':
                if not _equal(result, operation['value']): raise ValueError('test')
            else: result = None if op == 'remove' else deepcopy(operation['value'])
            continue
        parent = result
        for part in path[:-1]: parent = parent[_key(parent, part)]
        key = _key(parent, path[-1], op == 'add')
        if op == 'add':
            value = deepcopy(operation['value'])
            if isinstance(parent, list): parent.insert(key, value)
            else: parent[key] = value
        elif op == 'remove': del parent[key]
        elif op == 'replace':
            parent[key]
            parent[key] = deepcopy(operation['value'])
        elif not _equal(parent[key], operation['value']): raise ValueError('test')
    return result
''', [
"assert apply({'a': 1}, [{'op': 'replace', 'path': '/a', 'value': 2}]) == {'a': 2}",
"assert apply([1], [{'op': 'add', 'path': '/-', 'value': 2}]) == [1, 2]",
"assert apply({'a/b': {'~': 3}}, [{'op': 'remove', 'path': '/a~1b/~0'}]) == {'a/b': {}}",
"assert apply([1, 3], [{'op': 'add', 'path': '/1', 'value': 2}, {'op': 'remove', 'path': '/0'}]) == [2, 3]",
"assert apply(3, [{'op': 'add', 'path': '', 'value': {}}, {'op': 'add', 'path': '/', 'value': 2}]) == {'': 2}\nassert apply(3, [{'op': 'remove', 'path': ''}]) is None",
"for path in ['/01', '/-1', '/~2', 'bad']:\n    with pytest.raises(ValueError): apply([], [{'op': 'remove', 'path': path}])",
"for doc, path in [({}, '/x'), ([], '/0'), ({'a': 1}, '/a/x')]:\n    with pytest.raises(KeyError): apply(doc, [{'op': 'replace', 'path': path, 'value': 2}])",
"a = {'x': [1]}\nops = [{'op': 'replace', 'path': '/x/0', 'value': 2}, {'op': 'remove', 'path': '/missing'}]\nwith pytest.raises(KeyError): apply(a, ops)\nassert a == {'x': [1]}\nassert ops[0]['value'] == 2",
"with pytest.raises(ValueError): apply({'x': [True]}, [{'op': 'test', 'path': '', 'value': {'x': [1]}}])\nassert apply([1], [{'op': 'test', 'path': '/0', 'value': 1}]) == [1]\nwith pytest.raises(ValueError): apply({}, [{'op': 'wat', 'path': ''}])",
])

emit('overlay_delete', 'structured_changes', 2, 'fix', '''
# Repair layered object overlays
Fix `merge(base, layers)` for JSON-like values. Each layer is a dict. At a dict
key, the exact object `{'$delete': True}` deletes the key, without error if absent.
No other object is a deletion marker (in particular integer 1 is not True).
When old and new values are BOTH dicts, merge recursively; otherwise replace
with a deep copy, but a dict replacing a nondict is recursively interpreted
against an empty dict (so nested delete markers still apply). Lists replace
wholesale; markers inside lists are ordinary data. At the root base must be a
dict and layers must contain dicts, else ValueError. Layers apply in order.
Inputs and every returned mutable object are independent; no input mutation.
Keys are strings. Empty layers preserve a deep copy of base.
''', '''
from copy import deepcopy


def _delete(value):
    return isinstance(value, dict) and set(value) == {'$delete'} and value['$delete'] is True


def _overlay(base, layer):
    result = deepcopy(base)
    for key, value in layer.items():
        if _delete(value):
            result.pop(key, None)
        elif isinstance(value, dict):
            old = result.get(key)
            result[key] = _overlay(old if isinstance(old, dict) else {}, value)
        else:
            result[key] = deepcopy(value)
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
''', [
"assert merge({'a': 1}, [{'b': 2}]) == {'a': 1, 'b': 2}",
"assert merge({'a': {'b': 1}}, [{'a': {'c': 2}}]) == {'a': {'b': 1, 'c': 2}}",
"assert merge({'a': 1}, [{'a': {'$delete': True}}]) == {}",
"assert merge({}, [{'x': {'$delete': 1}}]) == {'x': {'$delete': 1}}",
"assert merge({'x': 1}, [{'x': {'gone': {'$delete': True}, 'ok': 2}}]) == {'x': {'ok': 2}}",
"assert merge({'a': [1]}, [{'a': [{'$delete': True}]}]) == {'a': [{'$delete': True}]}\nassert merge({}, [{'x': {'$delete': True, 'more': 1}}]) == {'x': {'$delete': True, 'more': 1}}",
"a = {'x': [1]}\nb = {'y': [2]}\nr = merge(a, [b])\nr['x'].append(3)\nr['y'].append(4)\nassert a == {'x': [1]} and b == {'y': [2]}",
"for base, layers in [([], []), ({}, [1])]:\n    with pytest.raises(ValueError): merge(base, layers)",
"assert merge({'a': 0}, iter([{'a': 1}, {'a': {'$delete': True}}, {'a': None}])) == {'a': None}\nassert merge({}, [{'missing': {'$delete': True}}]) == {}",
], start=[('task.py', "value['$delete'] is True", "value['$delete'] == True"), ('task.py', 'result[key] = deepcopy(value)', 'result[key] = value')])


emit('record_reconcile', 'structured_changes', 3, 'extend', '''
# Reconcile keyed records with renames
Extend `reconcile(old, new, renames=None)`. old/new are lists of dicts containing
unique string `id` fields, else ValueError. Return a list of operations:
`('remove', id)`, `('rename', old_id, new_id)`, `('update', id, changes)`, and
`('add', record)`. renames maps old IDs to distinct new IDs. Every source must
exist in old and every target in new; invalid maps raise ValueError. A target
may not collide with ANY different old ID, even one removed or renamed, so swaps
are invalid. Identity renames are allowed and emit nothing. Match renamed old
records to target IDs. First emit unmatched removals sorted by old ID, then
nonidentity renames sorted by source, then updates sorted by target ID, then
adds sorted by id. changes maps changed non-id fields to deep-copied new values;
removed fields map to `{'$missing': True}`. Compare nested values type-strictly
(True differs from 1 at any depth). Records may use any JSON-like values except
the reserved missing marker as field values. Neither input nor output shares
mutable values. Existing add/remove/update behavior with no renames stays.
''', '''
from copy import deepcopy


def _same(a, b):
    if type(a) is not type(b): return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
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
    a, b = _index(old), _index(new)
    renames = {} if renames is None else dict(renames)
    if len(set(renames.values())) != len(renames): raise ValueError('targets')
    for src, dst in renames.items():
        if src not in a or dst not in b or (dst in a and dst != src):
            raise ValueError('rename')
    mapped = {renames.get(key, key): value for key, value in a.items()}
    result = [('remove', key) for key in sorted(a) if renames.get(key, key) not in b]
    result += [('rename', src, dst) for src, dst in sorted(renames.items()) if src != dst]
    for ident in sorted(mapped.keys() & b.keys()):
        left, right = mapped[ident], b[ident]
        changes = {}
        for key in sorted((left.keys() | right.keys()) - {'id'}):
            if key not in right: changes[key] = {'$missing': True}
            elif key not in left or not _same(left[key], right[key]): changes[key] = deepcopy(right[key])
        if changes: result.append(('update', ident, changes))
    result += [('add', deepcopy(b[key])) for key in sorted(b.keys() - mapped.keys())]
    return result
''', [
"assert reconcile([{'id': 'a', 'v': 1}], [{'id': 'a', 'v': 2}]) == [('update', 'a', {'v': 2})]",
"assert reconcile([{'id': 'a'}], [{'id': 'b'}], {'a': 'b'}) == [('rename', 'a', 'b')]",
"assert reconcile([], [{'id': 'b'}, {'id': 'a'}]) == [('add', {'id': 'a'}), ('add', {'id': 'b'})]",
"assert reconcile([{'id': 'a', 'x': 1}], [{'id': 'b', 'y': 2}], {'a': 'b'}) == [('rename', 'a', 'b'), ('update', 'b', {'x': {'$missing': True}, 'y': 2})]",
"for r in [{'a': 'b', 'b': 'a'}, {'x': 'c'}, {'a': 'missing'}, {'a': 'c', 'b': 'c'}]:\n    with pytest.raises(ValueError): reconcile([{'id': 'a'}, {'id': 'b'}], [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}], r)",
"for rows in [[{'id': 'a'}, {'id': 'a'}], [{}], [{'id': 2}]]:\n    with pytest.raises(ValueError): reconcile(rows, [])",
"assert reconcile([{'id': 'a', 'x': [True]}], [{'id': 'a', 'x': [1]}]) == [('update', 'a', {'x': [1]})]",
"old = [{'id': 'z'}, {'id': 'a', 'v': 1}]\nnew = [{'id': 'b', 'v': [2]}, {'id': 'c'}]\nr = reconcile(old, new, {'a': 'b'})\nassert [x[0] for x in r] == ['remove', 'rename', 'update', 'add']\nr[2][2]['v'].append(3)\nassert new[0]['v'] == [2]",
"assert reconcile([{'id': 'a'}], [{'id': 'a'}], {'a': 'a'}) == []\nassert reconcile([{'id': 'b'}, {'id': 'a'}], []) == [('remove', 'a'), ('remove', 'b')]",
], start=[('task.py', 'renames = {} if renames is None else dict(renames)', "if renames:\n        raise NotImplementedError('rename mapping')\n    renames = {}")])

emit('three_way_tree', 'structured_changes', 4, 'implement', '''
# Three-way tree merge
Implement `merge(base, left, right)` returning `(merged, conflicts)`. JSON-like
values have string dict keys. Equality is recursive and type-strict. At any path,
if left == right take it; if left == base take right; if right == base take left.
Otherwise, when all PRESENT values at that path are dicts (at least left and
right must be present dicts), recursively merge their union of keys; an absent
base is treated as {}. Absence is distinct from None. All other concurrent
changes conflict: keep LEFT including its deletion. Record that path as a tuple
of dict keys, root as (). Lists are atomic, never merged element by element.
Missing keys on both sides disappear. Conflicts are sorted lexicographically;
record only the conflicting parent if recursion is not allowed, not descendants.
Return deeply independent values, never mutate inputs. Delete versus unchanged
is a deletion; delete versus modified is a conflict. If merged root were absent
it would be None, though all three supplied roots are always present.
''', '''
from copy import deepcopy

MISSING = object()


def _same(a, b):
    if a is MISSING or b is MISSING: return a is b
    if type(a) is not type(b): return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def merge(base, left, right):
    conflicts = []

    def clone(value):
        return MISSING if value is MISSING else deepcopy(value)

    def walk(b, l, r, path):
        if _same(l, r): return clone(l)
        if _same(l, b): return clone(r)
        if _same(r, b): return clone(l)
        if isinstance(l, dict) and isinstance(r, dict) and (b is MISSING or isinstance(b, dict)):
            b = {} if b is MISSING else b
            result = {}
            for key in sorted(b.keys() | l.keys() | r.keys()):
                value = walk(b.get(key, MISSING), l.get(key, MISSING), r.get(key, MISSING), path + (key,))
                if value is not MISSING: result[key] = value
            return result
        conflicts.append(path)
        return clone(l)

    result = walk(base, left, right, ())
    return (None if result is MISSING else result), sorted(conflicts)
''', [
"assert merge({'x': 1}, {'x': 2}, {'x': 1}) == ({'x': 2}, [])",
"assert merge({}, {'a': 1}, {'b': 2}) == ({'a': 1, 'b': 2}, [])",
"assert merge(0, 1, 2) == (1, [()])",
"assert merge({'x': 1}, {}, {'x': 2}) == ({}, [('x',)])\nassert merge({'x': 1}, {}, {'x': 1}) == ({}, [])",
"assert merge({}, {'x': {'a': 1}}, {'x': {'b': 2}}) == ({'x': {'a': 1, 'b': 2}}, [])",
"assert merge([0, 0], [1, 0], [0, 1]) == ([1, 0], [()])",
"assert merge({'x': None}, {}, {'x': None}) == ({}, [])\nassert merge({}, {'x': None}, {'x': 1}) == ({'x': None}, [('x',)])",
"assert merge({'a': [0]}, {'a': [True]}, {'a': [1]}) == ({'a': [True]}, [('a',)])\nassert merge({}, {'z': 1, 'a': 2}, {'z': 2, 'a': 3})[1] == [('a',), ('z',)]",
"b = {'x': {'y': [1]}}\nl = deepcopy(b)\nr = {'x': {'y': [2]}}\nout, c = merge(b, l, r)\nout['x']['y'].append(3)\nassert b['x']['y'] == [1] and r['x']['y'] == [2]\nassert c == []",
])
