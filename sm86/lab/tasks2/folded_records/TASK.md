# Repair folded log records
Fix `records(lines)` in `task.py`. Input is an iterable of strings without line
terminators. A header matches exactly `@DIGITS LEVEL: MESSAGE`, where DIGITS is
one or more ASCII digits, LEVEL is INFO/WARN/ERROR, and MESSAGE may be empty.
Output is a list of dicts with `seq` (integer), `level`, `message`, `tags` (list).
A line starting with one space continues the last record: remove exactly that
one space and append a newline plus the rest to its message. A line starting
`+tag ` attaches the remaining nonempty string as a tag, once per record in
first-seen order. Tags and continuations without a preceding header are errors.
A blank line or line starting `#` is ignored and does not clear the last record.
All other lines raise ValueError, including duplicate sequence numbers and
invalid headers. Records retain input order; returned objects never share tags.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
