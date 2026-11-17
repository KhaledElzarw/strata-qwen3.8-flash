# Streaming delimited records
Extend `Reader(separator=',')` with quoted fields across arbitrary `feed(chunk)`
boundaries. Separator is one character other than quote, CR or LF; otherwise
ValueError. `feed` returns complete records as lists of strings; `finish()`
returns the final unterminated record if there is one, then closes the reader.
Records end at LF or CRLF outside quotes; bare CR outside quotes is invalid.
CRLF may straddle chunks. Fields may be wholly double-quoted, doubled quotes
inside them mean one quote, and all characters (including CR/LF) inside quotes
are literal. A closing quote must be followed by separator, record end or EOF.
Quotes inside unquoted fields are invalid. Keep whitespace exactly. A blank
record is ['']; trailing separators give empty fields. Empty input gives no
records and a final record terminator creates no extra record. `finish` rejects
open quotes or pending bare CR. Calls after finish raise ValueError, including
empty feed and repeated finish. No recovery is required after invalid input.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
