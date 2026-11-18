from copy import deepcopy

class Coordinator:

    def __init__(self, clock):
        self.clock = clock
        self.leases = {}
        self.values = {}
        self.serial = 0

    def _live(self, resource, now):
        lease = self.leases.get(resource)
        return lease if lease and now < lease[2] else None

    def acquire(self, resource, owner, ttl):
        if ttl <= 0:
            raise ValueError('ttl')
        now = self.clock()
        lease = self._live(resource, now)
        if lease and lease[0] != owner:
            return None
        if lease:
            token = lease[1]
        else:
            self.serial += 1
            token = self.serial
        self.leases[resource] = (owner, token, now + ttl)
        return token

    def renew(self, resource, owner, token, ttl):
        if ttl <= 0:
            raise ValueError('ttl')
        now = self.clock()
        lease = self._live(resource, now)
        if not lease or lease[:2] != (owner, token):
            return False
        self.leases[resource] = (owner, token, now + ttl)
        return True

    def release(self, resource, owner, token):
        lease = self._live(resource, self.clock())
        if not lease or lease[:2] != (owner, token):
            return False
        del self.leases[resource]
        return True

    def write(self, resource, token, value):
        return self.write_many([(resource, token, value)])

    def write_many(self, items):
        items = list(items)
        names = [r for r, _, _ in items]
        if len(set(names)) != len(names):
            raise ValueError('duplicate')
        now = self.clock()
        for resource, token, _ in items:
            lease = self._live(resource, now)
            if not lease or lease[1] != token:
                return False
        updates = {r: deepcopy(v) for r, _, v in items}
        self.values.update(updates)
        return True

    def read(self, resource, default=None):
        if resource not in self.values:
            return default
        return deepcopy(self.values[resource])
