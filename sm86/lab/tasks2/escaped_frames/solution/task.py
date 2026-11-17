"""Incremental delimiter and escape framing.

Feed boundaries do not have protocol meaning.
Corrupt frames are counted and discarded."""

def encode(payload):
    """Construct one delimited checksum frame.

Escape reserved bytes in both payload and checksum.
Empty payloads still carry a checksum byte."""
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
        self.errors = 0
        self.inside = False
        self.escaped = False
        self.body = bytearray()

    def feed(self, data):
        """Consume bytes while preserving partial frame state.

A delimiter closes and restarts the framing window.
Only complete checksum-valid bodies are delivered."""
        result = []
        for byte in data:
            if byte == 126:
                if self.inside and (not self.escaped) and self.body:
                    if sum(self.body[:-1]) % 256 == self.body[-1]:
                        result.append(bytes(self.body[:-1]))
                if self.inside and (self.escaped or (self.body and sum(self.body[:-1]) % 256 != self.body[-1])):
                    self.errors += 1
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

    def reset(self):
        """Forget an unfinished frame without changing error history.

Returning outside the frame ignores subsequent noise.
The next delimiter begins a fresh body."""
        self.inside = False
        self.escaped = False
        self.body.clear()

    def finish(self):
        if self.inside and (self.body or self.escaped):
            self.errors += 1
        self.reset()
