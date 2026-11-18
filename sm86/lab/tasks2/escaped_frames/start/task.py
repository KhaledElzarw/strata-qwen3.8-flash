"""Incremental delimiter and escape framing.

Feed boundaries do not have protocol meaning.
Corrupt frames are counted and discarded."""

def encode(payload):
    """Construct one delimited checksum frame.

Escape reserved bytes in both payload and checksum.
Empty payloads still carry a checksum byte."""
    raise NotImplementedError()

class Decoder:

    def __init__(self):
        raise NotImplementedError()

    def feed(self, data):
        """Consume bytes while preserving partial frame state.

A delimiter closes and restarts the framing window.
Only complete checksum-valid bodies are delivered."""
        raise NotImplementedError()

    def reset(self):
        """Forget an unfinished frame without changing error history.

Returning outside the frame ignores subsequent noise.
The next delimiter begins a fresh body."""
        raise NotImplementedError()

    def finish(self):
        raise NotImplementedError()
