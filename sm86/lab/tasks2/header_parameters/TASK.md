# Header parameter parser
Implement `parse(text)` returning `(main, parameters)` for one header value.
The main value is the text before the first semicolon, stripped and lowercased;
it must be nonempty. Parameters are `; name = value`, with optional ASCII spaces
or tabs around punctuation and after the last value. Names match `[A-Za-z][A-Za-z0-9_-]*` and are lowercased;
duplicate names are errors. An unquoted value is a nonempty run of characters
other than semicolon, quote, backslash, space or tab. Quoted values use double
quotes and can be empty; backslash quotes exactly the next character (including
semicolon or backslash). Spaces inside quotes are preserved. Reject CR/LF
anywhere, trailing semicolons, malformed parameters, dangling escapes and
unclosed quotes with ValueError. Return parameters as a dict of decoded strings.

Add format_header(main, parameters): strip/lowercase nonempty main; reject
semicolon or CR/LF in main, invalid/duplicate case-insensitive parameter names,
or CR/LF in values with ValueError. Sort lowercase names lexically; quote every
value and escape backslash and quote. Join with semicolon and single space.
Values are strings. parse must round-trip this output.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
