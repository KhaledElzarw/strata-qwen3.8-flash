class Groups:

    def __init__(self, items):
        raise NotImplementedError()

    def representative(self, a):
        raise NotImplementedError()

    def connected(self, a, b):
        raise NotImplementedError()

    def size(self, a):
        raise NotImplementedError()

    def union(self, a, b):
        raise NotImplementedError()

    def snapshot(self):
        raise NotImplementedError()

    def rollback(self, mark):
        raise NotImplementedError()

    def members(self, a):
        raise NotImplementedError()
