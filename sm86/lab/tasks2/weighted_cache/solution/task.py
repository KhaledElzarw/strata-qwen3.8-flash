"""Weight-bounded recency with injected expiry time.

Each public operation uses one clock observation.
A live entry retains its insertion expiry on reads."""
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
        total = sum((v[1] for v in self.entries.values()))
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
        return sum((v[1] for v in self.entries.values()))

    def resize(self, budget):
        if budget <= 0:
            raise ValueError('budget')
        self._purge(self.clock())
        self.budget = budget
        total = sum((item[1] for item in self.entries.values()))
        while total > budget:
            _, (_, removed, _) = self.entries.popitem(last=False)
            total -= removed
