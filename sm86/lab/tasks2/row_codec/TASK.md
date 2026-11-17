# Extensible row codec preserving the text format
Extend encode(rows) / decode(text) with Codec(schema) instance methods
encode/decode. Legacy wrappers use default_codec = Codec(()), where empty
schema means all string fields and no width requirement. A schema is a tuple
of 'str', 'int', 'bool', or 'nullable'; invalid types raise ValueError. Nonempty
schema requires exact field count. Encoded rows are LF-separated, no trailing
LF; fields tab-separated. Escape backslash, tab, LF and CR as \\, \t, \n and \r
(two characters per escape). Empty text decodes to []; an empty single-field
row has no distinct encoding from no rows and is not tested. Reject unknown or
dangling escapes on decode with ValueError. Typed int accepts canonical decimal
strings on decode (0 or -?[1-9][0-9]*), and type exactly int on encode. bool maps
to 'true'/'false' (case sensitive) and requires bool values. nullable maps None
to raw '\N'; all non-None strings are escaped normally (literal '\N' round trips
as a string). str requires strings. Invalid fields raise ValueError. Decode
returns lists of lists. No caller mutation, each instance has independent schema.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
