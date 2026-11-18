# Nested conditional templates
Implement `render(template, values)` in `task.py`. Literal text is copied.
`{{name}}` inserts `str(values[name])`; name is stripped and matches
`[A-Za-z_][A-Za-z0-9_]*`. Blocks are `{% if name %}...{% else %}...{% end %}`;
else is optional. Nesting is allowed. Choose with bool(values[name]); only
chosen branch substitutions and conditions are evaluated. Missing evaluated
names raise KeyError. All template syntax, including unchosen branches, must be
validated: unmatched braces/tags, duplicate else, unknown directives and invalid
names raise ValueError. A literal `{` is allowed unless followed by `{` or `%`;
unmatched `}}` or `%}` is invalid. Tags allow arbitrary whitespace around their
words but no expressions. Empty templates and empty branches work. Do not modify
values. Do not use eval or exec. Syntax errors take precedence over missing names.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
