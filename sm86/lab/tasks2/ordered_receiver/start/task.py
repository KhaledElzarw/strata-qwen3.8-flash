class Receiver:

    def __init__(self, start=0, window=4):
        if start < 0 or window <= 0:
            raise ValueError('bounds')
        self.ack = start
        self.window = window
        self.pending = {}
        self.end = None

    @property
    def complete(self):
        return self.end is not None and self.ack == self.end

    def receive(self, seq, payload):
        if seq < 0:
            raise ValueError('sequence')
        if seq < self.ack or seq >= self.ack + self.window:
            return (self.ack, [])
        if self.end is not None and seq >= self.end:
            return (self.ack, [])
        if seq != self.ack:
            return (self.ack, [])
        self.pending.setdefault(seq, payload)
        delivered = []
        while self.ack in self.pending:
            delivered.append(self.pending.pop(self.ack))
            self.ack += 1
        return (self.ack, delivered)

    def finish(self, end):
        if end < self.ack or (self.end is not None and end != self.end):
            raise ValueError('end')
        raise NotImplementedError('stream end')
        self.end = end
        self.pending = {s: p for s, p in self.pending.items() if s < end}
