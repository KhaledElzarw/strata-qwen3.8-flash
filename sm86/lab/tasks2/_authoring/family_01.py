from common import emit

emit('coverage_bands', 'intervals', 2, 'implement', '''
# Coverage bands
Implement `bands(intervals, minimum=1)` in `task.py`. Each interval is an integer
half-open pair `(start, end)`. Reject reversed pairs and nonpositive minimum with
ValueError. Empty pairs contribute nothing. Duplicate intervals count separately.
Return sorted maximal `(start, end, count)` tuples where coverage is at least
minimum. Split whenever the count changes, but combine adjacent equal counts.
Events at the same endpoint happen together. Negative coordinates are valid.
Accept any iterable of pairs, consume it once, and never mutate caller data.
Implement `peak(intervals)` returning `(maximum_count, earliest_coordinate)`;
for no nonempty intervals return `(0, None)`. It uses the same validation.
''', '''
from collections import defaultdict


def bands(intervals, minimum=1):
    if minimum <= 0:
        raise ValueError('minimum')
    events = defaultdict(int)
    for start, end in intervals:
        if start > end:
            raise ValueError('reversed')
        if start != end:
            events[start] += 1
            events[end] -= 1
    result = []
    count = 0
    previous = None
    for point in sorted(events):
        if previous is not None and previous < point and count >= minimum:
            if result and result[-1][1] == previous and result[-1][2] == count:
                result[-1] = (result[-1][0], point, count)
            else:
                result.append((previous, point, count))
        count += events[point]
        previous = point
    return result


def peak(intervals):
    spans = bands(intervals)
    if not spans:
        return (0, None)
    best = max(count for _, _, count in spans)
    return best, next(start for start, _, count in spans if count == best)
''', [
"assert bands([(0, 4), (2, 6)]) == [(0, 2, 1), (2, 4, 2), (4, 6, 1)]",
"assert bands([(0, 2), (2, 4)]) == [(0, 4, 1)]",
"assert peak([(0, 3), (1, 2)]) == (2, 1)",
"assert bands([(1, 3)] * 3, 2) == [(1, 3, 3)]",
"assert bands([(-4, 0), (-2, 2)], 2) == [(-2, 0, 2)]",
"assert bands(iter([(0, 0), (2, 2)])) == []\nassert peak([]) == (0, None)",
"with pytest.raises(ValueError): bands([(3, 1)])\nwith pytest.raises(ValueError): bands([], 0)",
"a = [[4, 6], [0, 2]]\nb = deepcopy(a)\nassert peak(iter(a)) == (1, 0)\nassert a == b",
"assert bands([(0, 2), (0, 4), (2, 4)]) == [(0, 4, 2)]\nassert peak([(0, 2), (3, 5)]) == (1, 0)",
])

emit('room_assignment', 'intervals', 2, 'fix', '''
# Repair room assignment
Fix `assign(bookings)` and `conflicts(bookings)` in `task.py`. Bookings are an
iterable of `(id, start, end)` with distinct string IDs and integer times.
Reversed ranges or repeated IDs raise ValueError, including repeated empty
bookings. Inputs are never changed. Empty bookings receive room None and cause
no conflicts. Process nonempty bookings by `(start, end, id)`; reuse the smallest
available nonnegative room number, and a room is free at its previous end time.
`assign` returns a dict from every ID to its room. `conflicts` returns all
lexicographically sorted `(smaller_id, larger_id)` pairs whose nonempty
half-open intervals overlap. Touching intervals do not conflict.
''', '''
import heapq


def _read(bookings):
    items = list(bookings)
    seen = set()
    for ident, start, end in items:
        if ident in seen or start > end:
            raise ValueError('booking')
        seen.add(ident)
    return items


def assign(bookings):
    items = _read(bookings)
    active, free = [], []
    result = {i: None for i, s, e in items if s == e}
    rooms = 0
    for ident, start, end in sorted(items, key=lambda b: (b[1], b[2], b[0])):
        if start == end:
            continue
        while active and active[0][0] <= start:
            _, room = heapq.heappop(active)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
        else:
            room = rooms
            rooms += 1
        result[ident] = room
        heapq.heappush(active, (end, room))
    return result


def conflicts(bookings):
    items = _read(bookings)
    pairs = []
    for n, (a, s, e) in enumerate(items):
        for b, t, u in items[n + 1:]:
            if s < e and t < u and max(s, t) < min(e, u):
                pairs.append(tuple(sorted((a, b))))
    return sorted(pairs)
''', [
"assert assign([('a', 0, 3), ('b', 1, 2)]) == {'a': 0, 'b': 1}",
"assert conflicts([('z', 0, 3), ('a', 1, 4)]) == [('a', 'z')]",
"assert assign([]) == {}\nassert conflicts([]) == []",
"assert assign([('a', 0, 2), ('b', 2, 4)]) == {'a': 0, 'b': 0}",
"assert assign([('a', 0, 5), ('b', 1, 2), ('c', 5, 6)])['c'] == 0",
"assert conflicts([('a', 0, 2), ('b', 2, 4), ('c', 1, 1)]) == []",
"assert assign([('z', 1, 3), ('a', 1, 2), ('x', 1, 2)]) == {'a': 0, 'x': 1, 'z': 2}",
"for rows in [[('a', 0, 0), ('a', 1, 2)], [('a', 3, 1)]]:\n    for fn in [assign, conflicts]:\n        with pytest.raises(ValueError): fn(rows)",
"a = [('e', 2, 2), ('b', -2, 1), ('a', -1, 0)]\nb = a[:]\nassert assign(iter(a)) == {'e': None, 'b': 0, 'a': 1}\nassert conflicts(a) == [('a', 'b')]\nassert a == b",
], start=[('task.py', 'active[0][0] <= start', 'active[0][0] < start'), ('task.py', 'room = heapq.heappop(free)', 'room = free.pop()'), ('task.py', 'max(s, t) < min(e, u)', 'max(s, t) <= min(e, u)')])

emit('working_minutes', 'intervals', 3, 'extend', '''
# Working minutes with closures
Extend `Calendar` in `task.py` with blackout support and `advance`. Times and
lengths are integers. Constructor `Calendar(windows, blackouts=())` normalizes
half-open windows: drop empty ranges and merge overlap or touching endpoints.
Subtract the union of blackouts; reversed ranges anywhere raise ValueError.
`spans()` returns a fresh sorted list of resulting nonempty pairs.
`remaining(t)` counts working minutes at or after t.
`advance(t, minutes)` consumes working time starting at the first working instant
at or after t, skipping gaps. Negative minutes raise ValueError. Zero returns t
unchanged, even outside working time. Positive requests ending exactly at a span
end return that end, without jumping the next gap. Insufficient time raises
ValueError. Construction consumes each iterable once and no caller data is
mutated. Preserve the existing union and remaining behavior without blackouts.
''', '''
def _union(items):
    ranges = []
    for a, b in items:
        if a > b:
            raise ValueError('reversed')
        if a < b:
            ranges.append((a, b))
    result = []
    for a, b in sorted(ranges):
        if result and a <= result[-1][1]:
            result[-1] = result[-1][0], max(b, result[-1][1])
        else:
            result.append((a, b))
    return result


class Calendar:
    def __init__(self, windows, blackouts=()):
        available = _union(windows)
        for lo, hi in _union(blackouts):
            parts = []
            for a, b in available:
                if b <= lo or a >= hi:
                    parts.append((a, b))
                else:
                    if a < lo:
                        parts.append((a, lo))
                    if hi < b:
                        parts.append((hi, b))
            available = parts
        self._spans = available

    def spans(self):
        return list(self._spans)

    def remaining(self, t):
        return sum(max(0, b - max(a, t)) for a, b in self._spans)

    def advance(self, t, minutes):
        if minutes < 0:
            raise ValueError('negative duration')
        if minutes == 0:
            return t
        for a, b in self._spans:
            start = max(a, t)
            if start >= b:
                continue
            if minutes <= b - start:
                return start + minutes
            minutes -= b - start
        raise ValueError('insufficient working time')
''', [
"c = Calendar([(5, 10), (0, 5)])\nassert c.spans() == [(0, 10)]\nassert c.remaining(3) == 7",
"assert Calendar([(0, 10)], [(3, 7)]).spans() == [(0, 3), (7, 10)]",
"assert Calendar([(2, 5), (8, 12)]).advance(0, 5) == 10",
"c = Calendar([(2, 5), (8, 12)])\nassert c.advance(2, 3) == 5\nassert c.advance(5, 1) == 9",
"assert Calendar([]).advance(99, 0) == 99\nwith pytest.raises(ValueError): Calendar([]).advance(0, 1)",
"c = Calendar([(0, 10)], [(-3, 2), (4, 6), (5, 9), (10, 20)])\nassert c.spans() == [(2, 4), (9, 10)]\nassert c.remaining(3) == 2",
"with pytest.raises(ValueError): Calendar([(2, 1)])\nwith pytest.raises(ValueError): Calendar([], [(3, 2)])\nwith pytest.raises(ValueError): Calendar([]).advance(0, -1)",
"w = [[0, 10]]\nc = Calendar(iter(w), iter([(0, 3), (7, 10)]))\ns = c.spans()\ns.clear()\nassert c.spans() == [(3, 7)]\nassert w == [[0, 10]]",
"c = Calendar([(-5, -1), (2, 4)], [(-4, -2)])\nassert c.advance(-10, 4) == 4\nassert c.remaining(4) == 0\nwith pytest.raises(ValueError): c.advance(-10, 5)",
], start=[('task.py', 'for lo, hi in _union(blackouts):', 'for lo, hi in []:'), ('task.py', "if minutes < 0:", "raise NotImplementedError('advance is new')\n        if minutes < 0:")])

emit('weighted_agenda', 'intervals', 4, 'implement', '''
# Weighted agenda with deterministic ties
Implement `select(jobs, gap=0)`. A job is `(id, start, end, reward)`: distinct
string ID, integer times and integer reward. Reject duplicate IDs, start >= end,
or negative gap with ValueError before selecting. Accept any iterable; do not
mutate it. A chosen chronological sequence is compatible when each next start
is at least previous end + gap. Return `(total_reward, ids)` where ids is a tuple
in chronological `(start, end, id)` order. Maximize reward; on ties minimize the
number of jobs; then choose the lexicographically smallest chronological ID
tuple. Empty selection `(0, ())` is allowed. Negative and zero rewards may be
present. Handle at least 300 jobs without enumerating subsets. IDs are compared
as Python strings. Gap applies only between jobs, never at the outer boundaries.
''', '''
from bisect import bisect_right


def select(jobs, gap=0):
    if gap < 0:
        raise ValueError('gap')
    items = list(jobs)
    seen = set()
    for ident, start, end, reward in items:
        if ident in seen or start >= end:
            raise ValueError('job')
        seen.add(ident)
    items.sort(key=lambda j: (j[2], j[1], j[0]))
    ends = [j[2] for j in items]
    best = [(0, ())]
    for index, (ident, start, end, reward) in enumerate(items):
        previous = bisect_right(ends, start - gap, 0, index)
        total, ids = best[previous]
        take = total + reward, ids + (ident,)
        skip = best[-1]
        best.append(min((take, skip), key=lambda x: (-x[0], len(x[1]), x[1])))
    return best[-1]
''', [
"assert select([('a', 0, 3, 5), ('b', 1, 2, 4), ('c', 3, 4, 2)]) == (7, ('a', 'c'))",
"assert select([]) == (0, ())",
"assert select([('b', 0, 2, 5), ('a', 0, 2, 5)]) == (5, ('a',))",
"assert select([('a', 0, 1, 2), ('b', 1, 2, 3), ('z', 0, 2, 5)]) == (5, ('z',))",
"assert select([('z', 0, 1, 2), ('a', 2, 3, 2), ('c', 0, 3, 3)], gap=1) == (4, ('z', 'a'))",
"assert select([('a', 0, 1, 0), ('b', 1, 2, -2)]) == (0, ())",
"for jobs, gap in [([('a', 0, 0, 1)], 0), ([('a', 0, 1, 1)] * 2, 0), ([], -1)]:\n    with pytest.raises(ValueError): select(jobs, gap)",
"jobs = [('z', 2, 4, 3), ('b', 0, 2, 3), ('a', 0, 1, 3)]\nold = deepcopy(jobs)\nassert select(iter(jobs)) == (6, ('a', 'z'))\nassert jobs == old",
"jobs = [(str(i).zfill(3), i * 2, i * 2 + 1, 1) for i in range(300)]\nassert select(jobs) == (300, tuple(j[0] for j in jobs))",
])
