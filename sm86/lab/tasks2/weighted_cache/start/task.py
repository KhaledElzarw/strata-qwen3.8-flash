"""Weight-bounded recency with injected expiry time.

Each public operation uses one clock observation.
A live entry retains its insertion expiry on reads."""
from collections import OrderedDict

class Cache:

    def __init__(self, budget, clock):
        raise NotImplementedError()

    def _purge(self, now):
        raise NotImplementedError()

    def put(self, key, value, weight=1, ttl=None):
        raise NotImplementedError()

    def get(self, key, default=None):
        raise NotImplementedError()

    def __contains__(self, key):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()

    @property
    def weight(self):
        raise NotImplementedError()

    def resize(self, budget):
        raise NotImplementedError()
