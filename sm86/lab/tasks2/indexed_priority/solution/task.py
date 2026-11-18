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
        return (key, self.items[key][3])

    def pop(self):
        key, value = self.peek()
        heapq.heappop(self.heap)
        del self.items[key]
        return (key, value)

    def remove(self, key):
        if key not in self.items:
            return False
        del self.items[key]
        return True

    def __len__(self):
        return len(self.items)
