from common import emit

emit('event_dispatch', 'refactors', 2, 'extend', '''
# Event dispatcher with isolated instances
Extend the legacy `subscribe(topic, callback)`, `unsubscribe(topic, callback)`
and `emit(topic, value)` functions by adding `Bus` with the same methods, plus
`default_bus` used by all module wrappers. Subscribe returns True for a new
callback, False if already subscribed to that topic (identity comparison).
Unsubscribe returns bool. Emit returns callback results in subscription order;
callback exceptions propagate and stop dispatch. Dispatch uses a SNAPSHOT of
subscriptions: changes by callbacks affect the next emit, not the current one.
Add `once(topic, callback)` to Bus and module: one-shot subscriptions are removed
BEFORE invoking so recursive emit cannot invoke them twice. Re-subscribing an
already registered callback (once or normal) returns False without changing
its existing mode or order. Each Bus owns independent state. Topics are strings.
''', '''
class Bus:
    def __init__(self):
        self.handlers = {}

    def _add(self, topic, callback, once):
        handlers = self.handlers.setdefault(topic, [])
        if any(cb is callback for cb, _ in handlers):
            return False
        handlers.append((callback, once))
        return True

    def subscribe(self, topic, callback):
        return self._add(topic, callback, False)

    def once(self, topic, callback):
        return self._add(topic, callback, True)

    def unsubscribe(self, topic, callback):
        handlers = self.handlers.get(topic, [])
        for i, (cb, _) in enumerate(handlers):
            if cb is callback:
                del handlers[i]
                return True
        return False

    def emit(self, topic, value):
        result = []
        for callback, once in list(self.handlers.get(topic, [])):
            if once:
                self.unsubscribe(topic, callback)
            result.append(callback(value))
        return result


default_bus = Bus()


def subscribe(topic, callback): return default_bus.subscribe(topic, callback)
def unsubscribe(topic, callback): return default_bus.unsubscribe(topic, callback)
def emit(topic, value): return default_bus.emit(topic, value)
def once(topic, callback): return default_bus.once(topic, callback)
''', [
"b = Bus()\nf = lambda x: x+1\nassert b.subscribe('x', f)\nassert b.emit('x', 3) == [4]",
"b = Bus()\nf = lambda x: x\nassert b.subscribe('x', f)\nassert not b.subscribe('x', f)\nassert b.unsubscribe('x', f)",
"b = Bus()\nb.once('x', lambda v: v)\nassert b.emit('x', 1) == [1]\nassert b.emit('x', 2) == []",
"b = Bus()\nseen = []\ndef f(x):\n    b.unsubscribe('x', g)\n    return 'f'\ndef g(x): return 'g'\nb.subscribe('x', f)\nb.subscribe('x', g)\nassert b.emit('x', 0) == ['f', 'g']\nassert b.emit('x', 0) == ['f']",
"b = Bus()\nf = lambda x: b.emit('x', x)\nb.once('x', f)\nassert b.emit('x', 1) == [[]]",
"b = Bus()\ndef bad(x): raise RuntimeError('stop')\nb.once('x', bad)\nb.subscribe('x', lambda x: 4)\nwith pytest.raises(RuntimeError): b.emit('x', 0)\nassert b.emit('x', 0) == [4]",
"b = Bus()\nf = lambda x: 1\nb.once('x', f)\nassert not b.subscribe('x', f)\nb.emit('x', 0)\nassert b.emit('x', 0) == []",
"f = lambda x: x\nassert subscribe('legacy', f)\nassert default_bus.emit('legacy', 3) == [3]\nassert emit('legacy', 4) == [4]\nassert unsubscribe('legacy', f)\nassert Bus().emit('legacy', 1) == []",
"b = Bus()\ng = lambda x: 'g'\ndef f(x):\n    b.subscribe('x', g)\n    return 'f'\nb.subscribe('x', f)\nassert b.emit('x', 0) == ['f']\nassert b.emit('x', 0) == ['f', 'g']",
], start={'task.py': '''
_handlers = {}


def subscribe(topic, callback):
    handlers = _handlers.setdefault(topic, [])
    if any(cb is callback for cb in handlers):
        return False
    handlers.append(callback)
    return True


def unsubscribe(topic, callback):
    handlers = _handlers.get(topic, [])
    for i, cb in enumerate(handlers):
        if cb is callback:
            del handlers[i]
            return True
    return False


def emit(topic, value):
    return [cb(value) for cb in list(_handlers.get(topic, []))]


class Bus:
    def __init__(self):
        self.handlers = {}

    subscribe = staticmethod(subscribe)
    unsubscribe = staticmethod(unsubscribe)
    emit = staticmethod(emit)

    def once(self, topic, callback):
        raise NotImplementedError('one-shot')


default_bus = Bus()


def once(topic, callback):
    return default_bus.once(topic, callback)
'''})

emit('path_policy', 'refactors', 3, 'fix', '''
# Isolate path policy state while preserving legacy calls
Refactor task.py so `Policy(rules=())` instances own their rules. Preserve module
functions `add(pattern, allow)`, `check(path)`, `reset()` via `default_policy`.
Policy exposes those methods plus `rules()` returning a fresh list of pairs.
Patterns/paths are POSIX-style relative strings: collapse repeated '/' and '.';
reject absolute paths and ANY '..' segment with ValueError. A pattern may contain
`*` (one segment, including empty only if the entire path is empty) and `**`
(zero or more segments), each only as a whole segment; other embedded '*' is
invalid. Empty normalized pattern matches only empty path. Case sensitive.
Rules checked in insertion order, LAST matching rule wins; no match means False.
add validates pattern and requires bool allow, else ValueError without mutation.
Constructor accepts iterable of pairs, reset clears only that instance. Rules
returns normalized patterns. Preserve legacy functions' results for valid input.
Use fnmatch or your own matching but '*' must not cross slash boundaries.
''', '''
from functools import lru_cache


def _normalize(path, pattern=False):
    if path.startswith('/'):
        raise ValueError('absolute')
    parts = []
    for part in path.split('/'):
        if part == '..': raise ValueError('parent')
        if part in ('', '.'): continue
        if pattern and '*' in part and part not in ('*', '**'):
            raise ValueError('wildcard')
        parts.append(part)
    return '/'.join(parts)


def _matches(pattern, path):
    p = pattern.split('/') if pattern else []
    s = path.split('/') if path else []
    if p == ['*'] and not s: return True
    @lru_cache(None)
    def match(i, j):
        if i == len(p): return j == len(s)
        if p[i] == '**':
            return match(i + 1, j) or (j < len(s) and match(i, j + 1))
        return j < len(s) and (p[i] == '*' or p[i] == s[j]) and match(i + 1, j + 1)
    return match(0, 0)


class Policy:
    def __init__(self, rules=()):
        self._rules = []
        for pattern, allow in rules: self.add(pattern, allow)

    def add(self, pattern, allow):
        pattern = _normalize(pattern, True)
        if type(allow) is not bool: raise ValueError('allow')
        self._rules.append((pattern, allow))

    def check(self, path):
        path = _normalize(path)
        result = False
        for pattern, allow in self._rules:
            if _matches(pattern, path): result = allow
        return result

    def reset(self): self._rules.clear()
    def rules(self): return list(self._rules)


default_policy = Policy()


def add(pattern, allow): return default_policy.add(pattern, allow)
def check(path): return default_policy.check(path)
def reset(): return default_policy.reset()
''', [
"p = Policy([('src/*', True)])\nassert p.check('src/a') and not p.check('src/a/b')",
"p = Policy([('**', True), ('private/**', False)])\nassert not p.check('private/x') and p.check('a/b')",
"reset()\nadd('a', True)\nassert check('a') and default_policy.check('a')\nreset()",
"p = Policy([('a/**/b', True)])\nassert p.check('a/b') and p.check('a/x/y/b')",
"a, b = Policy(), Policy()\na.add('x', True)\nassert not b.check('x')\nb.reset()\nassert a.check('x')",
"p = Policy([('./a//b/', True)])\nassert p.rules() == [('a/b', True)]\nassert p.check('a/./b')\nr = p.rules()\nr.clear()\nassert p.check('a/b')",
"p = Policy([('a', True)])\nfor s in ['/a', 'a/../b', 'a*']:\n    with pytest.raises(ValueError): p.add(s, True)\nwith pytest.raises(ValueError): p.add('x', 1)\nassert p.rules() == [('a', True)]",
"p = Policy([('', True)])\nassert p.check('.') and not p.check('a')\nassert Policy([('*', True)]).check('')\nwith pytest.raises(ValueError): p.check('../a')",
"p = Policy([('**', True), ('**', False), ('A', True)])\nassert p.check('A') and not p.check('a')\np.reset()\nassert p.rules() == [] and not p.check('A')",
], start=[('task.py', 'self._rules = []', 'self._rules = _shared_rules'), ('task.py', 'from functools import lru_cache', 'from functools import lru_cache\n_shared_rules = []'), ('task.py', 'if _matches(pattern, path): result = allow', 'if _matches(pattern, path): return allow')])

emit('row_codec', 'refactors', 3, 'extend', r'''
# Extensible row codec preserving the text format
Extend encode(rows) / decode(text) with Codec(schema) instance methods
encode/decode. Legacy wrappers use default_codec = Codec(()), where empty
schema means all string fields and no width requirement. A schema is a tuple
of 'str', 'int', 'bool', or 'nullable'; invalid types raise ValueError. Nonempty
schema requires exact field count. Encoded rows are LF-separated, no trailing
LF; fields tab-separated. Escape backslash, tab, LF and CR as \\, \t, \n and \r
(two characters per escape). Empty text decodes to []; an empty single-field
row has no distinct encoding from no rows and is not tested. Reject unknown or
dangling escapes on decode with ValueError. Typed int accepts canonical decimal
strings on decode (0 or -?[1-9][0-9]*), and type exactly int on encode. bool maps
to 'true'/'false' (case sensitive) and requires bool values. nullable maps None
to raw '\N'; all non-None strings are escaped normally (literal '\N' round trips
as a string). str requires strings. Invalid fields raise ValueError. Decode
returns lists of lists. No caller mutation, each instance has independent schema.
''', r'''
import re


def _escape(text):
    return text.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')


def _unescape(text):
    out, i = [], 0
    escapes = {'\\': '\\', 't': '\t', 'n': '\n', 'r': '\r'}
    while i < len(text):
        ch = text[i]
        if ch == '\\':
            i += 1
            if i == len(text) or text[i] not in escapes: raise ValueError('escape')
            ch = escapes[text[i]]
        out.append(ch)
        i += 1
    return ''.join(out)


class Codec:
    def __init__(self, schema):
        self.schema = tuple(schema)
        if any(t not in ('str', 'int', 'bool', 'nullable') for t in self.schema):
            raise ValueError('schema')

    def _types(self, row):
        if self.schema and len(row) != len(self.schema): raise ValueError('width')
        return self.schema or ('str',) * len(row)

    def encode(self, rows):
        result = []
        for row in rows:
            fields = []
            for value, kind in zip(row, self._types(row)):
                if kind == 'nullable' and value is None: fields.append('\\N'); continue
                if kind == 'int' and type(value) is int: fields.append(str(value)); continue
                if kind == 'bool' and type(value) is bool: fields.append(str(value).lower()); continue
                if kind in ('str', 'nullable') and isinstance(value, str): fields.append(_escape(value)); continue
                raise ValueError('field')
            result.append('\t'.join(fields))
        return '\n'.join(result)

    def decode(self, text):
        result = []
        for line in text.split('\n') if text else []:
            row, fields = [], line.split('\t')
            for field, kind in zip(fields, self._types(fields)):
                if kind == 'nullable' and field == '\\N': row.append(None); continue
                value = _unescape(field)
                if kind == 'int':
                    if not re.fullmatch(r'0|-?[1-9][0-9]*', value): raise ValueError('integer')
                    value = int(value)
                elif kind == 'bool':
                    if value not in ('true', 'false'): raise ValueError('boolean')
                    value = value == 'true'
                row.append(value)
            result.append(row)
        return result


default_codec = Codec(())


def encode(rows): return default_codec.encode(rows)
def decode(text): return default_codec.decode(text)
''', [
"assert encode([['a', 'b'], ['c', 'd']]) == 'a\\tb\\nc\\td'\nassert decode('a\\tb') == [['a', 'b']]",
"c = Codec(('int', 'bool'))\nassert c.encode([[3, False]]) == '3\\tfalse'\nassert c.decode('-2\\ttrue') == [[-2, True]]",
 r'''c = Codec(('nullable', 'nullable'))
assert c.decode(c.encode([[None, r'\N']])) == [[None, r'\N']]''',
"rows = [['a\\tb', 'c\\nd', 'e\\rf', 'g\\\\h']]\nassert decode(encode(rows)) == rows",
"for s in ['00', '-0', '+1', ' 1', '1.0']:\n    with pytest.raises(ValueError): Codec(('int',)).decode(s)",
"for s in ['True', '1', 'FALSE']:\n    with pytest.raises(ValueError): Codec(('bool',)).decode(s)\nwith pytest.raises(ValueError): Codec(('int',)).encode([[True]])",
 r'''for s in [r'a\q', 'a' + chr(92)]:
    with pytest.raises(ValueError): decode(s)
with pytest.raises(ValueError): Codec(('int', 'str')).decode('1')''',
"assert decode('') == []\nassert Codec(('int',)).encode([]) == ''\nwith pytest.raises(ValueError): Codec(('bad',))\nwith pytest.raises(ValueError): Codec(('str',)).encode([[1]])",
"rows = [[1, 'x']]\na = Codec(('int', 'str'))\nb = Codec(('str',))\nassert a.decode(a.encode(rows)) == rows\nassert rows == [[1, 'x']]\nassert b.decode('2') == [['2']]",
], start=[('task.py', "if any(t not in ('str', 'int', 'bool', 'nullable') for t in self.schema):", "if self.schema:\n            raise NotImplementedError('typed schemas')\n        if any(t not in ('str', 'int', 'bool', 'nullable') for t in self.schema):")])

emit('scoped_registry', 'refactors', 4, 'extend', '''
# Scoped command registry with compatibility wrappers
Refactor `register`, `invoke`, `names` module functions to delegate to
`default_registry` of new class `Registry(parent=None)`. A registry owns local
commands and aliases; parent is another Registry or None. `register(name, fn)`
requires nonempty string name, callable fn, and no LOCAL name collision (including
aliases), else ValueError. `alias(name, target)` requires nonempty string names
and no local collision, but may refer to missing/future targets. Child definitions
shadow inherited names. `invoke(name, *args, **kwargs)` resolves aliases from the
ORIGINAL invoking registry, even when alias itself was inherited; missing name
raises KeyError and any alias cycle raises ValueError. Call fn with exactly the
supplied args/kwargs, propagating exceptions and returning its result. `names()`
returns sorted union of local and inherited names including unresolved aliases.
`unregister(name)` removes only local entries, returning bool; an inherited
entry may become visible again. Add module alias/unregister wrappers too.
Parent state never changes through child mutation. Existing function invocation
behavior must remain, and separate root registries never share state.
''', '''
class Registry:
    def __init__(self, parent=None):
        self.parent = parent
        self.local = {}

    def _name(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError('name')

    def register(self, name, fn):
        self._name(name)
        if name in self.local or not callable(fn): raise ValueError('command')
        self.local[name] = ('function', fn)

    def alias(self, name, target):
        self._name(name)
        self._name(target)
        if name in self.local: raise ValueError('collision')
        self.local[name] = ('alias', target)

    def _lookup(self, name):
        if name in self.local: return self.local[name]
        if self.parent is not None: return self.parent._lookup(name)
        raise KeyError(name)

    def invoke(self, name, *args, **kwargs):
        seen = set()
        while True:
            if name in seen: raise ValueError('alias cycle')
            seen.add(name)
            kind, value = self._lookup(name)
            if kind == 'function': return value(*args, **kwargs)
            name = value

    def names(self):
        inherited = self.parent.names() if self.parent is not None else []
        return sorted(set(inherited) | self.local.keys())

    def unregister(self, name):
        if name not in self.local: return False
        del self.local[name]
        return True


default_registry = Registry()


def register(name, fn): return default_registry.register(name, fn)
def invoke(name, *args, **kwargs): return default_registry.invoke(name, *args, **kwargs)
def names(): return default_registry.names()
def alias(name, target): return default_registry.alias(name, target)
def unregister(name): return default_registry.unregister(name)
''', [
"r = Registry()\nr.register('add', lambda a, b=1: a+b)\nassert r.invoke('add', 2, b=3) == 5",
"r = Registry()\nr.alias('a', 'b')\nr.register('b', lambda: 7)\nassert r.invoke('a') == 7",
"p = Registry()\np.register('x', lambda: 1)\nc = Registry(p)\nassert c.invoke('x') == 1",
"p = Registry()\np.register('x', lambda: 1)\np.alias('a', 'x')\nc = Registry(p)\nc.register('x', lambda: 2)\nassert c.invoke('a') == 2 and p.invoke('a') == 1",
"r = Registry()\nr.alias('a', 'b')\nr.alias('b', 'a')\nwith pytest.raises(ValueError): r.invoke('a')\nwith pytest.raises(KeyError): r.invoke('missing')",
"p = Registry()\np.register('x', lambda: 1)\nc = Registry(p)\nassert not c.unregister('x')\nc.register('x', lambda: 2)\nassert c.unregister('x')\nassert c.invoke('x') == 1",
"r = Registry()\nr.alias('z', 'future')\nr.register('a', lambda: 1)\nassert r.names() == ['a', 'z']\nwith pytest.raises(ValueError): r.register('a', lambda: 2)\nwith pytest.raises(ValueError): r.alias('a', 'b')\nwith pytest.raises(ValueError): r.register('', lambda: 2)\nwith pytest.raises(ValueError): r.register('b', 2)",
"register('legacy', lambda x: x*2)\nalias('legacy_alias', 'legacy')\nassert invoke('legacy_alias', 3) == 6\nassert default_registry.invoke('legacy', 2) == 4\nassert names() == ['legacy', 'legacy_alias']\nassert unregister('legacy')\nassert Registry().names() == []",
"r = Registry()\ndef fail(): raise RuntimeError('boom')\nr.register('bad', fail)\nwith pytest.raises(RuntimeError): r.invoke('bad')\np = Registry()\np.alias('a', 'b')\nc = Registry(p)\nc.alias('b', 'a')\nwith pytest.raises(ValueError): c.invoke('a')",
], start=[('task.py', "if name in self.local: return self.local[name]\n        if self.parent is not None: return self.parent._lookup(name)", "if name in self.local: return self.local[name]"), ('task.py', 'def alias(self, name, target):\n        self._name(name)', "def alias(self, name, target):\n        raise NotImplementedError('aliases')\n        self._name(name)")])
