from common import emit

emit('escaped_frames', 'protocols', 2, 'implement', '''
# Escaped byte frames
Implement `encode(payload)` and `Decoder.feed(data)` for bytes. A frame starts
and ends with byte 126; body is payload followed by checksum sum(payload) % 256.
In body, bytes 126 and 125 are escaped as 125 followed by original XOR 32.
Decoder ignores bytes outside frames. Each delimiter ends the current frame
and ALSO starts the next (shared delimiters work). An empty body is ignored;
checksum-only body yields b''. Invalid checksum or dangling escape at delimiter
discards that frame, then resynchronizes. Any byte after escape is XOR-decoded.
`feed` returns a list of complete valid payload bytes; state survives arbitrary
chunks, including an escape split across calls. Separate decoders share no state.
No decoding error is raised for corrupt frames. encode always uses two delimiters.
''', '''
def encode(payload):
    body = payload + bytes([sum(payload) % 256])
    result = bytearray([126])
    for byte in body:
        if byte in (125, 126):
            result.extend((125, byte ^ 32))
        else:
            result.append(byte)
    result.append(126)
    return bytes(result)


class Decoder:
    def __init__(self):
        self.inside = False
        self.escaped = False
        self.body = bytearray()

    def feed(self, data):
        result = []
        for byte in data:
            if byte == 126:
                if self.inside and not self.escaped and self.body:
                    if sum(self.body[:-1]) % 256 == self.body[-1]:
                        result.append(bytes(self.body[:-1]))
                self.inside = True
                self.body.clear()
                self.escaped = False
            elif self.inside:
                if self.escaped:
                    self.body.append(byte ^ 32)
                    self.escaped = False
                elif byte == 125:
                    self.escaped = True
                else:
                    self.body.append(byte)
        return result
''', [
"assert encode(b'AB') == bytes([126, 65, 66, 131, 126])",
"assert Decoder().feed(encode(b'hello')) == [b'hello']",
"assert Decoder().feed(encode(b'')) == [b'']",
"d = Decoder()\nout = []\nfor b in encode(bytes([125, 126])): out.extend(d.feed(bytes([b])))\nassert out == [bytes([125, 126])]",
"assert Decoder().feed(b'noise' + bytes([126, 1, 2, 126]) + encode(b'good')) == [b'good']",
"a, b = encode(b'a'), encode(b'b')\nassert Decoder().feed(a + b[1:]) == [b'a', b'b']",
"assert Decoder().feed(bytes([126, 1, 125, 126]) + encode(b'x')) == [b'x']",
"d = Decoder()\nassert d.feed(b'~~~') == []\nassert d.feed(encode(b'x')[:-1]) == []\nassert d.feed(b'~') == [b'x']\nassert Decoder().feed(b'') == []",
"for payload in [bytes(range(256)), b'~'*3, b'}'*4, bytes([126])]:\n    assert Decoder().feed(encode(payload)) == [payload]",
])

emit('nested_transactions', 'protocols', 2, 'fix', '''
# Repair nested key transactions
Fix `Store(initial=None)` in `task.py`. Initial is a dict copied deeply. `begin()`
opens a nested transaction; `commit()` keeps changes and closes ONLY the innermost
transaction, and `rollback()` restores the innermost begin snapshot. Either
closing method with no transaction raises ValueError. `set(key, value)` deep
copies its value; `get(key)` returns a deep copy, raising KeyError when missing.
`delete(key)` removes a key or raises KeyError. `snapshot()` is a deep copy of
current contents; `depth` is the count of open transactions. Rolling back an
outer transaction also undoes inner commits. Operations outside transactions
work immediately. Instances, snapshots and supplied mutable values are isolated.
''', '''
from copy import deepcopy


class Store:
    def __init__(self, initial=None):
        self.data = deepcopy({} if initial is None else initial)
        self.saved = []

    @property
    def depth(self):
        return len(self.saved)

    def begin(self):
        self.saved.append(deepcopy(self.data))

    def commit(self):
        if not self.saved:
            raise ValueError('no transaction')
        self.saved.pop()

    def rollback(self):
        if not self.saved:
            raise ValueError('no transaction')
        self.data = self.saved.pop()

    def set(self, key, value):
        self.data[key] = deepcopy(value)

    def get(self, key):
        return deepcopy(self.data[key])

    def delete(self, key):
        del self.data[key]

    def snapshot(self):
        return deepcopy(self.data)
''', [
"s = Store({'a': 1})\ns.begin()\ns.set('a', 2)\ns.rollback()\nassert s.get('a') == 1",
"s = Store()\ns.begin()\ns.set('a', 1)\ns.commit()\nassert s.snapshot() == {'a': 1}",
"assert Store().depth == 0",
"s = Store({'a': 1})\ns.begin()\ns.set('a', 2)\ns.begin()\ns.set('a', 3)\ns.commit()\nassert s.depth == 1\ns.rollback()\nassert s.get('a') == 1",
"s = Store()\ns.begin()\ns.set('a', 1)\ns.begin()\ns.delete('a')\ns.rollback()\nassert s.get('a') == 1\ns.commit()",
"for method in ['commit', 'rollback']:\n    with pytest.raises(ValueError): getattr(Store(), method)()",
"v = {'a': [1]}\ns = Store(v)\nv['a'].append(2)\nx = s.get('a')\nx.append(3)\nassert s.get('a') == [1]",
"s = Store()\nv = [1]\ns.set('x', v)\nv.append(2)\na = s.snapshot()\na['x'].clear()\nassert s.get('x') == [1]\nassert Store().snapshot() == {}",
"s = Store()\nwith pytest.raises(KeyError): s.get('x')\nwith pytest.raises(KeyError): s.delete('x')\ns.begin()\ns.begin()\ns.rollback()\nassert s.depth == 1",
], start=[('task.py', 'self.saved.pop()\n\n    def rollback', 'self.saved.clear()\n\n    def rollback'), ('task.py', 'return deepcopy(self.data[key])', 'return self.data[key]'), ('task.py', 'self.data[key] = deepcopy(value)', 'self.data[key] = value')])

emit('ordered_receiver', 'protocols', 3, 'extend', '''
# Bounded out-of-order receiver
Extend `Receiver(start=0, window=4)` with buffering and end-of-stream support.
start is nonnegative and window positive, else ValueError. `receive(seq, payload)`
accepts nonnegative integer seq and bytes payload; seq < 0 raises ValueError.
Return `(ack, delivered)`, where ack is the next expected sequence and delivered
is a list of payloads newly released in order. Old seq < ack is ignored. Buffer
only seq < ack + window; further packets are ignored. First payload for a
buffered seq wins. Each accepted call drains every contiguous buffered packet.
`finish(end)` declares exclusive stream end; end < ack or a repeated DIFFERENT
end raises ValueError with no change. Repeating the same end is allowed. Discard
buffered seq >= end. After finish, packets >= end are ignored; packets below
end may fill holes. `complete` is true exactly when end is declared and ack ==
end. Calling finish returns no value. Existing in-order behavior must remain.
''', '''
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
            return self.ack, []
        if self.end is not None and seq >= self.end:
            return self.ack, []
        self.pending.setdefault(seq, payload)
        delivered = []
        while self.ack in self.pending:
            delivered.append(self.pending.pop(self.ack))
            self.ack += 1
        return self.ack, delivered

    def finish(self, end):
        if end < self.ack or (self.end is not None and end != self.end):
            raise ValueError('end')
        self.end = end
        self.pending = {s: p for s, p in self.pending.items() if s < end}
''', [
"r = Receiver()\nassert r.receive(0, b'a') == (1, [b'a'])",
"r = Receiver()\nassert r.receive(1, b'b') == (0, [])\nassert r.receive(0, b'a') == (2, [b'a', b'b'])",
"r = Receiver()\nr.finish(0)\nassert r.complete",
"r = Receiver(window=2)\nassert r.receive(2, b'far') == (0, [])\nassert r.receive(0, b'a') == (1, [b'a'])\nassert r.receive(1, b'b') == (2, [b'b'])",
"r = Receiver()\nr.receive(1, b'first')\nr.receive(1, b'second')\nassert r.receive(0, b'a') == (2, [b'a', b'first'])\nassert r.receive(0, b'x') == (2, [])",
"r = Receiver()\nr.receive(3, b'c')\nr.finish(2)\nr.receive(1, b'b')\nassert r.receive(0, b'a') == (2, [b'a', b'b'])\nassert r.complete\nassert r.receive(2, b'x') == (2, [])",
"r = Receiver(start=3)\nassert not r.complete\nr.finish(4)\nr.finish(4)\nwith pytest.raises(ValueError): r.finish(5)\nassert r.receive(3, b'') == (4, [b''])\nassert r.complete",
"for kw in [{'start': -1}, {'window': 0}]:\n    with pytest.raises(ValueError): Receiver(**kw)\nr = Receiver()\nwith pytest.raises(ValueError): r.receive(-1, b'x')\nr.receive(0, b'a')\nwith pytest.raises(ValueError): r.finish(0)",
"r = Receiver(window=5)\nfor s in [4, 2, 3, 1]: r.receive(s, bytes([s]))\nassert r.receive(0, b'z') == (5, [b'z', b'\\x01', b'\\x02', b'\\x03', b'\\x04'])\nassert Receiver().ack == 0",
], start=[('task.py', 'self.pending.setdefault(seq, payload)', "if seq != self.ack:\n            return self.ack, []\n        self.pending.setdefault(seq, payload)"), ('task.py', 'self.end = end\n        self.pending', "raise NotImplementedError('stream end')\n        self.end = end\n        self.pending")])

emit('lease_fencing', 'protocols', 4, 'implement', '''
# Lease fencing and atomic writes
Implement `Coordinator(clock)` in task.py using helper modules if useful. clock
is an injected nondecreasing callable returning integer time; never use real time.
`acquire(resource, owner, ttl)` requires ttl > 0 (ValueError otherwise). A live
lease held by another owner returns None. Same owner acquisition renews expiry
from now and keeps its token. An absent or expired lease gets a globally
increasing positive integer token; tokens are never reused across resources.
A lease is expired at now >= expires. `renew(resource, owner, token, ttl)` returns
True only on matching live lease, setting expiry to now + ttl. Invalid ttl always
raises ValueError. `release(resource, owner, token)` returns True only for a
matching live lease and removes it. `write(resource, token, value)` returns True
only if token equals that resource's live lease token; store a deep copy.
`read(resource, default=None)` returns a deep copy of last written value, surviving
release and expiry; default is returned as given when no value exists.
`write_many(items)` takes iterable `(resource, token, value)`; validate all leases
at ONE clock reading, then deep-copy and commit all writes atomically. Duplicate
resources raise ValueError before any write; any stale token returns False with
no writes. Empty batch succeeds. Individual instances share nothing.
''', '''
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
        self.leases[resource] = owner, token, now + ttl
        return token

    def renew(self, resource, owner, token, ttl):
        if ttl <= 0:
            raise ValueError('ttl')
        now = self.clock()
        lease = self._live(resource, now)
        if not lease or lease[:2] != (owner, token):
            return False
        self.leases[resource] = owner, token, now + ttl
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
''', [
"c = Coordinator(lambda: 0)\nt = c.acquire('x', 'a', 5)\nassert t == 1\nassert c.acquire('x', 'b', 5) is None\nassert c.write('x', t, 7) and c.read('x') == 7",
"now = [0]\nc = Coordinator(lambda: now[0])\nt = c.acquire('x', 'a', 5)\nnow[0] = 5\nassert not c.write('x', t, 1)\nassert c.acquire('x', 'a', 2) == 2",
"c = Coordinator(lambda: 0)\nt = c.acquire('x', 'a', 2)\nassert c.release('x', 'a', t)\nassert not c.release('x', 'a', t)",
"now = [0]\nc = Coordinator(lambda: now[0])\nt = c.acquire('x', 'a', 2)\nnow[0] = 1\nassert c.acquire('x', 'a', 5) == t\nnow[0] = 5\nassert c.renew('x', 'a', t, 2)\nnow[0] = 7\nassert not c.renew('x', 'a', t, 2)",
"c = Coordinator(lambda: 0)\na = c.acquire('a', 'o', 2)\nb = c.acquire('b', 'o', 2)\nassert (a, b) == (1, 2)\nassert not c.write('b', a, 3)",
"c = Coordinator(lambda: 0)\nt = c.acquire('x', 'a', 2)\nassert not c.write_many([('x', t, 3), ('missing', 1, 4)])\nassert c.read('x') is None\nwith pytest.raises(ValueError): c.write_many([('x', t, 1), ('x', t, 2)])",
"c = Coordinator(lambda: 0)\nt = c.acquire('x', 'a', 2)\nv = [1]\nassert c.write('x', t, v)\nv.append(2)\nw = c.read('x')\nw.append(3)\nc.release('x', 'a', t)\nassert c.read('x') == [1]\ndefault = []\nassert c.read('absent', default) is default",
"c = Coordinator(lambda: 0)\nfor ttl in [0, -1]:\n    with pytest.raises(ValueError): c.acquire('x', 'a', ttl)\n    with pytest.raises(ValueError): c.renew('x', 'a', 1, ttl)\nassert not c.release('x', 'a', 1)\nassert c.write_many([])",
"calls = [0]\ndef clk():\n    calls[0] += 1\n    return calls[0]\nc = Coordinator(clk)\na = c.acquire('a', 'o', 10)\nb = c.acquire('b', 'o', 10)\nbefore = calls[0]\nassert c.write_many(iter([('a', a, 1), ('b', b, 2)]))\nassert calls[0] == before + 1\nassert c.read('a') == 1 and c.read('b') == 2",
])
