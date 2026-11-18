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
        a, b = (self.representative(a), self.representative(b))
        if a == b:
            return False
        if (self.sizes[a], -self.order[a]) < (self.sizes[b], -self.order[b]):
            a, b = (b, a)
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
        return frozenset((x for x in self.parent if self.representative(x) == root))
