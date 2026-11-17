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

Decoder exposes errors, initially 0: count each NONEMPTY body with invalid
checksum, or any dangling escape at delimiter. Empty delimiter runs are not
errors. reset() clears framing state but keeps errors. finish() discards an
unfinished nonempty frame or dangling escape, counting one error, then resets
framing. It returns None and may be repeated.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
