class Quota:

    def __init__(self, capacity, window, clock):
        if capacity <= 0 or window <= 0:
            raise ValueError('bounds')
        self.capacity, self.window, self.clock = (capacity, window, clock)
        self.entries = {}

    def _purge(self, now):
        self.entries = {k: v for k, v in self.entries.items() if now < v[2]}

    def _total(self):
        return sum((v[0] for v in self.entries.values()))

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
