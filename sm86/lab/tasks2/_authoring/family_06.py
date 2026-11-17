from common import emit

emit('prefix_catalog', 'structures', 2, 'implement', '''
# Weighted prefix catalog
Implement `Catalog`. `put(word, weight)` inserts/replaces a nonempty string with
nonnegative integer weight; invalid word or weight raises ValueError. `remove(word)`
returns bool. `suggest(prefix='', limit=5)` returns matching words by descending
weight then lexical word; negative limit raises ValueError. Empty prefix matches
all; limit 0 returns []. `prefix_weight(prefix)` sums matching weights, counting
zero-weight entries as present. `longest(text)` returns the longest stored word
that is a prefix of text, or None. Exact Unicode/case-sensitive comparisons.
`len(catalog)` counts words; replacing never changes count. Instances share no
state. Return fresh lists. A dict or trie is acceptable; no complexity target.
''', '''
class Catalog:
    def __init__(self):
        self.words = {}

    def put(self, word, weight):
        if not isinstance(word, str) or not word or type(weight) is not int or weight < 0:
            raise ValueError('word or weight')
        self.words[word] = weight

    def remove(self, word):
        if word not in self.words:
            return False
        del self.words[word]
        return True

    def suggest(self, prefix='', limit=5):
        if limit < 0:
            raise ValueError('limit')
        matching = (w for w in self.words if w.startswith(prefix))
        return sorted(matching, key=lambda w: (-self.words[w], w))[:limit]

    def prefix_weight(self, prefix):
        return sum(v for w, v in self.words.items() if w.startswith(prefix))

    def longest(self, text):
        matching = [w for w in self.words if text.startswith(w)]
        return max(matching, key=len) if matching else None

    def __len__(self):
        return len(self.words)
''', [
"c = Catalog()\nc.put('cat', 2)\nc.put('car', 3)\nassert c.suggest('ca') == ['car', 'cat']",
"c = Catalog()\nc.put('a', 1)\nc.put('ab', 2)\nassert c.longest('abcd') == 'ab'",
"c = Catalog()\nc.put('x', 0)\nassert c.remove('x')\nassert not c.remove('x')",
"c = Catalog()\nfor w in ['b', 'a', 'c']: c.put(w, 2)\nassert c.suggest('', 2) == ['a', 'b']\nassert c.suggest('', 0) == []",
"c = Catalog()\nc.put('a', 2)\nc.put('a', 5)\nassert len(c) == 1 and c.prefix_weight('a') == 5",
"c = Catalog()\nc.put('a', 0)\nassert c.suggest() == ['a']\nassert c.longest('ax') == 'a'\nassert c.prefix_weight('z') == 0",
"for w, v in [('', 1), ('a', -1), ('a', True), (3, 2)]:\n    with pytest.raises(ValueError): Catalog().put(w, v)\nwith pytest.raises(ValueError): Catalog().suggest(limit=-1)",
"c = Catalog()\nc.put('é', 1)\nc.put('E', 2)\nassert c.suggest() == ['E', 'é']\nassert c.longest('É') is None",
"c = Catalog()\nc.put('abc', 2)\nc.put('abd', 4)\nc.put('x', 9)\na = c.suggest('ab')\na.clear()\nassert c.prefix_weight('ab') == 6\nassert c.suggest('ab') == ['abd', 'abc']\nassert len(Catalog()) == 0",
])

emit('indexed_priority', 'structures', 3, 'fix', '''
# Repair stable indexed priority updates
Fix `Priority`. `put(key, priority, value)` inserts or updates. Items pop in
ascending numeric priority order, ties by FIRST insertion order. Updates keep
that order; removal followed by reinsertion gets new order. `pop()` returns
`(key, value)` and removes it, or raises KeyError when empty. `peek()` is the same
without removal. `remove(key)` returns bool; `len(queue)` counts live items.
Keys are arbitrary hashable objects, values arbitrary objects; neither may be
compared to break ties. Obsolete heap records from updates/removal must never
resurrect an entry or pop its replacement incorrectly. Empty peek raises
KeyError too. Independent instances share no state.
''', '''
import heapq


class Priority:
    def __init__(self):
        self.heap = []
        self.items = {}
        self.serial = 0
        self.version = 0

    def put(self, key, priority, value):
        if key in self.items:
            order = self.items[key][1]
        else:
            self.serial += 1
            order = self.serial
        self.version += 1
        self.items[key] = (priority, order, self.version, value)
        heapq.heappush(self.heap, (priority, order, self.version, key))

    def _clean(self):
        while self.heap:
            p, order, version, key = self.heap[0]
            item = self.items.get(key)
            if item is not None and item[:3] == (p, order, version):
                return
            heapq.heappop(self.heap)

    def peek(self):
        self._clean()
        if not self.heap:
            raise KeyError('empty')
        key = self.heap[0][3]
        return key, self.items[key][3]

    def pop(self):
        key, value = self.peek()
        heapq.heappop(self.heap)
        del self.items[key]
        return key, value

    def remove(self, key):
        if key not in self.items:
            return False
        del self.items[key]
        return True

    def __len__(self):
        return len(self.items)
''', [
"p = Priority()\np.put('a', 2, 1)\np.put('b', 1, 2)\nassert p.pop() == ('b', 2)",
"p = Priority()\np.put('a', 1, 2)\nassert p.peek() == ('a', 2) and len(p) == 1",
"p = Priority()\np.put('a', 1, 2)\nassert p.remove('a')\nassert not p.remove('a')",
"p = Priority()\np.put('a', 1, 'old')\np.put('b', 1, 'b')\np.put('a', 1, 'new')\nassert p.pop() == ('a', 'new')",
"p = Priority()\np.put('a', 0, 'old')\np.put('a', 10, 'new')\np.put('b', 5, 'b')\nassert p.pop() == ('b', 'b')\nassert p.pop() == ('a', 'new')",
"p = Priority()\np.put('a', 1, 1)\np.put('b', 1, 2)\np.remove('a')\np.put('a', 1, 3)\nassert p.pop() == ('b', 2)",
"p = Priority()\np.put(None, 1, {})\np.put(2, 1, [])\nassert p.pop() == (None, {})\nassert p.pop() == (2, [])",
"p = Priority()\np.put('a', 0, 1)\np.put('a', 1, 2)\np.remove('a')\nwith pytest.raises(KeyError): p.peek()\nwith pytest.raises(KeyError): p.pop()\nassert len(p) == 0",
"p = Priority()\nfor i in range(30): p.put('x', 30-i, i)\nassert p.pop() == ('x', 29)\nwith pytest.raises(KeyError): p.pop()\nassert len(Priority()) == 0",
], start=[('task.py', 'order = self.items[key][1]', 'self.serial += 1\n            order = self.serial'), ('task.py', 'item[:3] == (p, order, version)', 'True')])

emit('range_paint', 'structures', 4, 'extend', '''
# Range map paint, erase and query
Extend `RangeMap` in task.py. Initially no integer points are assigned. `paint(lo,
hi, value)` assigns every point in half-open [lo,hi), overwriting prior values.
Add `erase(lo, hi)` which makes the range unassigned, and `query(lo, hi)` which
returns sorted clipped `(start, end, value)` spans of assigned points there.
`spans()` returns full maximal spans, combining adjacent equal values. Values
are strings or None; None is an ASSIGNED value, not an empty marker. All methods
with ranges reject lo > hi with ValueError and make no change; lo == hi does
nothing / returns []. `get(point, default=None)` returns assigned value or
default, preserving distinction via custom default. Negative coordinates work.
Do not enumerate points: bounds can exceed 10**12. Query/spans return fresh lists.
Keep paint/get compatibility; erase must split spans and queries must clip.
''', '''
class RangeMap:
    def __init__(self):
        self.parts = []

    def _bounds(self, lo, hi):
        if lo > hi:
            raise ValueError('bounds')

    def _normalize(self, parts):
        result = []
        for a, b, value in sorted(parts, key=lambda p: p[0]):
            if result and result[-1][1] == a and result[-1][2] == value:
                result[-1] = (result[-1][0], b, value)
            else:
                result.append((a, b, value))
        self.parts = result

    def erase(self, lo, hi):
        self._bounds(lo, hi)
        if lo == hi:
            return
        kept = []
        for a, b, value in self.parts:
            if b <= lo or a >= hi:
                kept.append((a, b, value))
            else:
                if a < lo:
                    kept.append((a, lo, value))
                if hi < b:
                    kept.append((hi, b, value))
        self._normalize(kept)

    def paint(self, lo, hi, value):
        self._bounds(lo, hi)
        if lo == hi:
            return
        self.erase(lo, hi)
        self._normalize(self.parts + [(lo, hi, value)])

    def get(self, point, default=None):
        for a, b, value in self.parts:
            if a <= point < b:
                return value
        return default

    def spans(self):
        return list(self.parts)

    def query(self, lo, hi):
        self._bounds(lo, hi)
        return [(max(a, lo), min(b, hi), v) for a, b, v in self.parts
                if max(a, lo) < min(b, hi)]
''', [
"r = RangeMap()\nr.paint(0, 5, 'a')\nassert r.get(2) == 'a'\nassert r.get(5, 'x') == 'x'",
"r = RangeMap()\nr.paint(0, 5, 'a')\nr.erase(2, 3)\nassert r.spans() == [(0, 2, 'a'), (3, 5, 'a')]",
"r = RangeMap()\nr.paint(0, 10, 'a')\nassert r.query(3, 6) == [(3, 6, 'a')]",
"r = RangeMap()\nr.paint(0, 10, 'a')\nr.paint(3, 7, 'b')\nassert r.spans() == [(0, 3, 'a'), (3, 7, 'b'), (7, 10, 'a')]",
"r = RangeMap()\nr.paint(0, 3, None)\nr.paint(3, 5, None)\nassert r.spans() == [(0, 5, None)]\nassert r.get(1, 'missing') is None",
"r = RangeMap()\nr.paint(-10**12, 10**12, 'a')\nr.erase(-1, 1)\nassert r.query(-2, 2) == [(-2, -1, 'a'), (1, 2, 'a')]",
"r = RangeMap()\nr.paint(0, 3, 'a')\nfor f in [lambda: r.paint(2, 1, 'b'), lambda: r.erase(2, 1), lambda: r.query(2, 1)]:\n    with pytest.raises(ValueError): f()\nassert r.spans() == [(0, 3, 'a')]",
"r = RangeMap()\nr.paint(0, 2, 'a')\nr.erase(1, 1)\nr.paint(1, 1, 'b')\nassert r.query(1, 1) == []\ns = r.spans()\ns.clear()\nassert r.spans() == [(0, 2, 'a')]",
"r = RangeMap()\nr.paint(0, 10, 'a')\nr.paint(2, 8, 'b')\nr.paint(2, 8, 'a')\nassert r.spans() == [(0, 10, 'a')]\nr.erase(-1, 11)\nassert r.spans() == []",
], start=[('task.py', 'def erase(self, lo, hi):', 'def _erase(self, lo, hi):'), ('task.py', 'self.erase(lo, hi)', 'self._erase(lo, hi)'), ('task.py', 'def query(self, lo, hi):', "def erase(self, lo, hi):\n        raise NotImplementedError('erase')\n\n    def query(self, lo, hi):\n        raise NotImplementedError('query')")])

emit('rollback_groups', 'structures', 4, 'implement', '''
# Rollback connectivity groups
Implement `Groups(items)` for distinct hashable items (duplicates raise ValueError).
`union(a,b)` returns True if groups merged, False if already connected.
`connected(a,b)` and `size(a)` query; unknown items raise KeyError before mutation.
`count` counts components. `snapshot()` returns a nonnegative integer history
position. Each successful union adds ONE position; redundant union adds none.
`rollback(mark)` undoes successful unions after mark, rejecting noninteger marks
(including bool), negative marks and marks beyond current position with ValueError
and no changes. Reusing a position after branching is allowed: marks denote
positions, not immutable versions. `members(a)` returns a frozenset of a's group.
Support at least 1000 items and nested rollbacks. Avoid full state copies per
union: use union by size and a change log; do not compress paths unless undoable.
Construction order decides roots on equal sizes (root from earlier item wins),
but expose `representative(a)` returning that root item to make this deterministic.
''', '''
class Groups:
    def __init__(self, items):
        items = list(items)
        if len(set(items)) != len(items):
            raise ValueError('duplicate')
        self.order = {x: i for i, x in enumerate(items)}
        self.parent = {x: x for x in items}
        self.sizes = {x: 1 for x in items}
        self.history = []
        self.count = len(items)

    def representative(self, a):
        if a not in self.parent:
            raise KeyError(a)
        while self.parent[a] != a:
            a = self.parent[a]
        return a

    def connected(self, a, b):
        return self.representative(a) == self.representative(b)

    def size(self, a):
        return self.sizes[self.representative(a)]

    def union(self, a, b):
        a, b = self.representative(a), self.representative(b)
        if a == b:
            return False
        if (self.sizes[a], -self.order[a]) < (self.sizes[b], -self.order[b]):
            a, b = b, a
        self.history.append((b, a, self.sizes[a]))
        self.parent[b] = a
        self.sizes[a] += self.sizes[b]
        self.count -= 1
        return True

    def snapshot(self):
        return len(self.history)

    def rollback(self, mark):
        if type(mark) is not int or not 0 <= mark <= len(self.history):
            raise ValueError('mark')
        while len(self.history) > mark:
            child, parent, old_size = self.history.pop()
            self.parent[child] = child
            self.sizes[parent] = old_size
            self.count += 1

    def members(self, a):
        root = self.representative(a)
        return frozenset(x for x in self.parent if self.representative(x) == root)
''', [
"g = Groups('abc')\nassert g.union('a', 'b')\nassert g.connected('a', 'b')\nassert g.size('a') == 2 and g.count == 2",
"g = Groups('abc')\nm = g.snapshot()\ng.union('a', 'b')\ng.rollback(m)\nassert not g.connected('a', 'b')",
"g = Groups('ab')\nassert g.union('a', 'b')\nassert not g.union('b', 'a')\nassert g.snapshot() == 1",
"g = Groups('abcd')\ng.union('a', 'b')\nm = g.snapshot()\ng.union('c', 'd')\ng.union('b', 'd')\ng.rollback(m)\nassert g.members('a') == frozenset('ab')\nassert g.size('c') == 1",
"g = Groups(['z', 'a', 'b', 'c'])\ng.union('a', 'z')\ng.union('c', 'b')\ng.union('c', 'a')\nassert g.representative('c') == 'z'",
"g = Groups('abc')\ng.union('a', 'b')\ng.rollback(0)\ng.union('b', 'c')\ng.rollback(1)\nassert g.members('b') == frozenset('bc')",
"g = Groups('a')\nfor m in [-1, 1, True, 0.0]:\n    with pytest.raises(ValueError): g.rollback(m)\nwith pytest.raises(KeyError): g.union('a', 'x')\nassert g.snapshot() == 0",
"with pytest.raises(ValueError): Groups(['a', 'a'])\ng = Groups([])\nassert g.count == 0\ng.rollback(0)",
"g = Groups(range(1000))\nfor i in range(1, 1000): g.union(i-1, i)\nassert g.size(999) == 1000 and g.representative(999) == 0\ng.rollback(500)\nassert g.size(0) == 501 and g.count == 500",
])
