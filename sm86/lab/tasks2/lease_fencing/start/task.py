from copy import deepcopy

class Coordinator:

    def __init__(self, clock):
        raise NotImplementedError()

    def _live(self, resource, now):
        raise NotImplementedError()

    def acquire(self, resource, owner, ttl):
        raise NotImplementedError()

    def renew(self, resource, owner, token, ttl):
        raise NotImplementedError()

    def release(self, resource, owner, token):
        raise NotImplementedError()

    def write(self, resource, token, value):
        raise NotImplementedError()

    def write_many(self, items):
        raise NotImplementedError()

    def read(self, resource, default=None):
        raise NotImplementedError()
