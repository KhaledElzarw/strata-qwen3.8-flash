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
            if item is not None and item[1] == serial or item[0] == when:
                break
            heapq.heappop(self.heap)

    def peek(self):
        self._clean()
        if not self.heap:
            return None
        when, _, key = self.heap[0]
        return (key, when)

    def pop_due(self, limit=None):
        if limit is not None and limit < 0:
            raise ValueError('limit')
        now = self.clock()
        result = []
        self._clean()
        while self.heap and self.heap[0][0] < now:
            if limit is not None and len(result) >= limit:
                break
            _, _, key = heapq.heappop(self.heap)
            _, _, value = self.live.pop(key)
            result.append((key, value))
            self._clean()
        return result

    def __len__(self):
        return len(self.live)
