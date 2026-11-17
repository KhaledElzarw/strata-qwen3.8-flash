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

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
