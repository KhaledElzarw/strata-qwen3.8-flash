from common import emit

emit('weighted_cache', 'timed_state', 2, 'implement', '''
# Weight-bounded cache
Implement `Cache(budget, clock)` with positive integer budget, else ValueError.
`put(key, value, weight=1, ttl=None)` requires positive weight and ttl None or
nonnegative; invalid arguments raise ValueError before altering anything. Purge
all expired entries first. Replace an existing key, then evict least recently
used entries until total weight <= budget. An oversized entry is not stored,
but DOES remove an older value of the same key. ttl=0 expires immediately;
expiry is now >= insertion_time + ttl. get(key, default=None) purges expiry and
makes a hit most recent without extending ttl. contains via `key in cache`
purges but does not affect recency. `keys()` returns live keys least to most
recent; `weight` returns live total weight. Read time once per public operation.
Values are stored by reference; instances are independent. clock is injected.
''', '''
from collections import OrderedDict


class Cache:
    def __init__(self, budget, clock):
        if budget <= 0:
            raise ValueError('budget')
        self.budget = budget
        self.clock = clock
        self.entries = OrderedDict()

    def _purge(self, now):
        for key, (_, _, end) in list(self.entries.items()):
            if end is not None and now >= end:
                del self.entries[key]

    def put(self, key, value, weight=1, ttl=None):
        if weight <= 0 or (ttl is not None and ttl < 0):
            raise ValueError('weight or ttl')
        now = self.clock()
        self._purge(now)
        self.entries.pop(key, None)
        if weight > self.budget or ttl == 0:
            return
        self.entries[key] = (value, weight, None if ttl is None else now + ttl)
        total = sum(v[1] for v in self.entries.values())
        while total > self.budget:
            _, (_, removed, _) = self.entries.popitem(last=False)
            total -= removed

    def get(self, key, default=None):
        self._purge(self.clock())
        if key not in self.entries:
            return default
        self.entries.move_to_end(key)
        return self.entries[key][0]

    def __contains__(self, key):
        self._purge(self.clock())
        return key in self.entries

    def keys(self):
        self._purge(self.clock())
        return list(self.entries)

    @property
    def weight(self):
        self._purge(self.clock())
        return sum(v[1] for v in self.entries.values())
''', [
"c = Cache(3, lambda: 0)\nc.put('a', 1, 2)\nc.put('b', 2)\nassert c.weight == 3 and c.keys() == ['a', 'b']",
"c = Cache(2, lambda: 0)\nc.put('a', 1)\nc.put('b', 2)\nc.get('a')\nc.put('c', 3)\nassert c.keys() == ['a', 'c']",
"t = [0]\nc = Cache(2, lambda: t[0])\nc.put('a', 1, ttl=2)\nt[0] = 2\nassert c.get('a', 9) == 9",
"c = Cache(2, lambda: 0)\nc.put('a', 1)\nc.put('b', 2)\nassert 'a' in c\nc.put('c', 3)\nassert c.keys() == ['b', 'c']",
"c = Cache(2, lambda: 0)\nc.put('a', 1)\nc.put('a', 2, 3)\nassert c.keys() == []\nc.put('b', 2, ttl=0)\nassert c.weight == 0",
"t = [0]\nc = Cache(3, lambda: t[0])\nc.put('old', 0, ttl=2)\nc.put('live', 1)\nt[0] = 2\nc.put('new', 2, 2)\nassert c.keys() == ['live', 'new']",
"with pytest.raises(ValueError): Cache(0, lambda: 0)\nc = Cache(2, lambda: 0)\nc.put('a', 1)\nfor kw in [{'weight': 0}, {'ttl': -1}]:\n    with pytest.raises(ValueError): c.put('a', 2, **kw)\nassert c.get('a') == 1",
"t = [0]\nc = Cache(2, lambda: t[0])\nc.put('a', 1, ttl=3)\nt[0] = 2\nc.get('a')\nt[0] = 3\nassert c.weight == 0",
"calls = []\ndef clock():\n    calls.append(1)\n    return 0\nc = Cache(2, clock)\nc.put('a', None)\nassert c.get('a', 9) is None\nassert c.keys() == ['a']\nassert len(calls) == 3",
])

emit('deadline_queue', 'timed_state', 3, 'fix', '''
# Repair a reschedulable deadline queue
Fix `Queue(clock)`. `schedule(key, when, value)` inserts or replaces a key.
`cancel(key)` returns True if pending, else False. `pop_due(limit=None)` returns
`(key, value)` pairs due at when <= clock(), ordered by deadline then scheduling
sequence. Every replacement gets a NEW sequence even when its deadline stays
the same. A stale heap entry must never release a replacement early or twice.
limit None means unlimited; nonnegative integer limit caps returned live items,
not stale heap entries. Negative limit raises ValueError without changes.
`peek()` returns earliest live `(key, when)` or None, even if not due.
`len(queue)` counts live keys. Values and keys may be mutually unorderable
hashable objects, so never compare them for ordering. clock is injected and
pop_due reads it once. cancel and peek must ignore stale heap entries.
''', '''
import heapq


class Queue:
    def __init__(self, clock):
        self.clock = clock
        self.heap = []
        self.live = {}
        self.serial = 0

    def schedule(self, key, when, value):
        self.serial += 1
        self.live[key] = (when, self.serial, value)
        heapq.heappush(self.heap, (when, self.serial, key))

    def cancel(self, key):
        if key not in self.live:
            return False
        del self.live[key]
        return True

    def _clean(self):
        while self.heap:
            when, serial, key = self.heap[0]
            item = self.live.get(key)
            if item is not None and item[:2] == (when, serial):
                break
            heapq.heappop(self.heap)

    def peek(self):
        self._clean()
        if not self.heap:
            return None
        when, _, key = self.heap[0]
        return key, when

    def pop_due(self, limit=None):
        if limit is not None and limit < 0:
            raise ValueError('limit')
        now = self.clock()
        result = []
        self._clean()
        while self.heap and self.heap[0][0] <= now:
            if limit is not None and len(result) >= limit:
                break
            _, _, key = heapq.heappop(self.heap)
            _, _, value = self.live.pop(key)
            result.append((key, value))
            self._clean()
        return result

    def __len__(self):
        return len(self.live)
''', [
"q = Queue(lambda: 5)\nq.schedule('a', 3, 1)\nassert q.peek() == ('a', 3)\nassert q.pop_due() == [('a', 1)]",
"q = Queue(lambda: 0)\nq.schedule('a', 1, 2)\nassert q.cancel('a')\nassert not q.cancel('a')\nassert q.peek() is None",
"q = Queue(lambda: 10)\nq.schedule('a', 1, 2)\nq.schedule('b', 2, 3)\nassert q.pop_due(1) == [('a', 2)]\nassert len(q) == 1",
"t = [1]\nq = Queue(lambda: t[0])\nq.schedule('a', 1, 'old')\nq.schedule('a', 5, 'new')\nassert q.pop_due() == []\nt[0] = 5\nassert q.pop_due() == [('a', 'new')]",
"q = Queue(lambda: 2)\nq.schedule('a', 2, 1)\nassert q.pop_due() == [('a', 1)]",
"q = Queue(lambda: 3)\nq.schedule('a', 1, 1)\nq.schedule('b', 1, 2)\nq.schedule('a', 1, 3)\nassert q.pop_due() == [('b', 2), ('a', 3)]",
"q = Queue(lambda: 5)\nq.schedule('a', 1, 1)\nq.cancel('a')\nq.schedule('b', 2, 2)\nassert q.pop_due(0) == []\nassert q.pop_due(1) == [('b', 2)]",
"q = Queue(lambda: 9)\nq.schedule(None, 1, {})\nq.schedule(1, 1, [])\nassert q.pop_due() == [(None, {}), (1, [])]",
"q = Queue(lambda: 2)\nq.schedule('a', 1, 1)\nwith pytest.raises(ValueError): q.pop_due(-1)\nassert q.peek() == ('a', 1)\nassert q.pop_due() == [('a', 1)]\nassert q.peek() is None",
], start=[('task.py', 'item[:2] == (when, serial)', 'item[1] == serial or item[0] == when'), ('task.py', 'self.heap[0][0] <= now', 'self.heap[0][0] < now')])

emit('rolling_quota', 'timed_state', 3, 'extend', '''
# Rolling quota with reservations
Extend `Quota(capacity, window, clock)`. capacity and window must be positive,
else ValueError. Committed requests are retained in the rolling interval
(now-window, now], so expiry at exactly window is removed. Add reservations:
`reserve(key, amount=1, ttl=None)` returns True if total live amount + amount <=
capacity. amount positive, ttl None or positive; invalid arguments or a repeated
LIVE key raise ValueError, before changing live usage. A reservation expires at
ttl if supplied, otherwise after window; ttl may exceed window. `commit(key)`
turns a live reservation into committed usage timestamped NOW, returning True;
missing/expired/already committed key returns False. Committed records keep key
occupied until window expiry. `cancel(key)` removes only live reservations,
returning bool. `used` counts committed and reserved amounts. Purge expiry before
operations and read clock once per call. Existing `take(amount=1)` atomically
adds anonymous committed usage if it fits; False otherwise. Never spend on
failed calls. clock is injected and nondecreasing.
''', '''
class Quota:
    def __init__(self, capacity, window, clock):
        if capacity <= 0 or window <= 0:
            raise ValueError('bounds')
        self.capacity, self.window, self.clock = capacity, window, clock
        self.entries = {}

    def _purge(self, now):
        self.entries = {k: v for k, v in self.entries.items() if now < v[2]}

    def _total(self):
        return sum(v[0] for v in self.entries.values())

    @property
    def used(self):
        self._purge(self.clock())
        return self._total()

    def take(self, amount=1):
        if amount <= 0:
            raise ValueError('amount')
        now = self.clock()
        self._purge(now)
        if self._total() + amount > self.capacity:
            return False
        self.entries[object()] = (amount, 'committed', now + self.window)
        return True

    def reserve(self, key, amount=1, ttl=None):
        if amount <= 0 or (ttl is not None and ttl <= 0):
            raise ValueError('amount or ttl')
        now = self.clock()
        self._purge(now)
        if key in self.entries:
            raise ValueError('duplicate')
        if self._total() + amount > self.capacity:
            return False
        self.entries[key] = (amount, 'reserved', now + (self.window if ttl is None else ttl))
        return True

    def commit(self, key):
        now = self.clock()
        self._purge(now)
        item = self.entries.get(key)
        if item is None or item[1] != 'reserved':
            return False
        self.entries[key] = (item[0], 'committed', now + self.window)
        return True

    def cancel(self, key):
        self._purge(self.clock())
        item = self.entries.get(key)
        if item is None or item[1] != 'reserved':
            return False
        del self.entries[key]
        return True
''', [
"q = Quota(2, 5, lambda: 0)\nassert q.take(2)\nassert not q.take()\nassert q.used == 2",
"q = Quota(2, 5, lambda: 0)\nassert q.reserve('a')\nassert q.commit('a')\nassert not q.commit('a')",
"q = Quota(2, 5, lambda: 0)\nq.reserve('a')\nassert q.cancel('a')\nassert q.used == 0",
"t = [0]\nq = Quota(2, 5, lambda: t[0])\nq.take()\nq.reserve('a', ttl=2)\nt[0] = 2\nassert q.used == 1\nassert not q.commit('a')\nt[0] = 5\nassert q.used == 0",
"t = [0]\nq = Quota(1, 5, lambda: t[0])\nq.reserve('a')\nt[0] = 4\nassert q.commit('a')\nt[0] = 8\nassert q.used == 1\nt[0] = 9\nassert q.used == 0",
"q = Quota(2, 5, lambda: 0)\nq.reserve('a')\nwith pytest.raises(ValueError): q.reserve('a')\nq.commit('a')\nwith pytest.raises(ValueError): q.reserve('a')\nassert not q.cancel('a')\nassert q.used == 1",
"for cap, win in [(0, 1), (1, 0)]:\n    with pytest.raises(ValueError): Quota(cap, win, lambda: 0)\nq = Quota(2, 5, lambda: 0)\nfor amount, ttl in [(0, None), (1, 0), (-1, 2)]:\n    with pytest.raises(ValueError): q.reserve('a', amount, ttl)\nassert q.used == 0",
"t = [0]\nq = Quota(1, 2, lambda: t[0])\nassert q.reserve('a', ttl=10)\nt[0] = 3\nassert q.used == 1\nassert not q.reserve('b')\nassert not q.cancel('b')",
"t = [0]\nq = Quota(1, 2, lambda: t[0])\nq.reserve('a')\nt[0] = 2\nassert q.reserve('a')\nassert q.used == 1",
], start=[('task.py', "if amount <= 0 or (ttl is not None and ttl <= 0):", "raise NotImplementedError('reservations')\n        if amount <= 0 or (ttl is not None and ttl <= 0):"), ('task.py', 'def commit(self, key):\n        now', "def commit(self, key):\n        raise NotImplementedError('commit')\n        now"), ('task.py', 'def cancel(self, key):\n        self._purge', "def cancel(self, key):\n        raise NotImplementedError('cancel')\n        self._purge")])

emit('worker_schedule', 'timed_state', 4, 'implement', '''
# Dependency worker schedule
Implement `schedule(jobs, workers)` returning sorted `(id, worker, start, end)`
tuples in `(start, worker, id)` order. jobs maps string IDs to `(duration, deps)`;
duration is a positive integer, deps an iterable of IDs (duplicates ignored).
workers is positive, else ValueError. Unknown dependencies raise KeyError; any
cycle raises ValueError, even in disconnected components. Do not mutate inputs.
Time begins at zero; all jobs finishing at time t release dependencies BEFORE
new starts at t. Whenever workers are free, assign ready jobs in lexical ID
order to the smallest free worker IDs (0 through workers-1). Running jobs are
never interrupted. Advance time to the next completion when no further start is
possible. Return [] for empty jobs. Validate all input before scheduling. Handle
at least 200 jobs without enumerating possible schedules. No actual clocks.
''', '''
import heapq


def schedule(jobs, workers):
    if workers <= 0:
        raise ValueError('workers')
    deps = {j: set(v[1]) for j, v in jobs.items()}
    for j, (duration, _) in jobs.items():
        if duration <= 0:
            raise ValueError('duration')
        for parent in deps[j]:
            if parent not in jobs:
                raise KeyError(parent)
    children = {j: [] for j in jobs}
    left = {j: len(d) for j, d in deps.items()}
    for j, parents in deps.items():
        for parent in parents:
            children[parent].append(j)
    ready = [j for j in jobs if not left[j]]
    heapq.heapify(ready)
    free = list(range(workers))
    running, result = [], []
    now = 0
    while ready or running:
        while ready and free:
            job = heapq.heappop(ready)
            worker = heapq.heappop(free)
            end = now + jobs[job][0]
            result.append((job, worker, now, end))
            heapq.heappush(running, (end, worker, job))
        if not running:
            break
        now = running[0][0]
        while running and running[0][0] == now:
            _, worker, job = heapq.heappop(running)
            heapq.heappush(free, worker)
            for child in children[job]:
                left[child] -= 1
                if left[child] == 0:
                    heapq.heappush(ready, child)
    if len(result) != len(jobs):
        raise ValueError('cycle')
    return sorted(result, key=lambda r: (r[2], r[1], r[0]))
''', [
"assert schedule({'a': (2, []), 'b': (1, ['a'])}, 2) == [('a', 0, 0, 2), ('b', 0, 2, 3)]",
"assert schedule({}, 1) == []",
"assert schedule({'b': (2, []), 'a': (1, [])}, 2) == [('a', 0, 0, 1), ('b', 1, 0, 2)]",
"j = {'a': (2, []), 'b': (2, []), 'c': (1, ['b']), 'd': (1, ['a'])}\nassert schedule(j, 2)[2:] == [('c', 0, 2, 3), ('d', 1, 2, 3)]",
"j = {'a': (4, []), 'b': (1, []), 'c': (1, [])}\nassert schedule(j, 2) == [('a', 0, 0, 4), ('b', 1, 0, 1), ('c', 1, 1, 2)]",
"with pytest.raises(ValueError): schedule({'a': (1, ['b']), 'b': (1, ['a']), 'z': (1, [])}, 2)\nwith pytest.raises(KeyError): schedule({'a': (1, ['x'])}, 2)",
"with pytest.raises(ValueError): schedule({}, 0)\nwith pytest.raises(ValueError): schedule({'a': (0, [])}, 1)",
"j = {'a': (1, []), 'b': (1, ['a', 'a'])}\nold = deepcopy(j)\nassert schedule(j, 1)[1] == ('b', 0, 1, 2)\nassert j == old",
"j = {f'j{i:03}': (1, [] if i == 0 else [f'j{i-1:03}']) for i in range(200)}\nr = schedule(j, 4)\nassert len(r) == 200 and r[-1] == ('j199', 0, 199, 200)",
])
