# Weighted prefix catalog
Implement `Catalog`. `put(word, weight)` inserts/replaces a nonempty string with
nonnegative integer weight (a bool is not a valid weight); invalid word or weight raises ValueError. `remove(word)`
returns bool. `suggest(prefix='', limit=5)` returns matching words by descending
weight then lexical word; negative limit raises ValueError. Empty prefix matches
all; limit 0 returns []. `prefix_weight(prefix)` sums matching weights, counting
zero-weight entries as present. `longest(text)` returns the longest stored word
that is a prefix of text, or None. Exact Unicode/case-sensitive comparisons.
`len(catalog)` counts words; replacing never changes count. Instances share no
state. Return fresh lists. A dict or trie is acceptable; no complexity target.

Add match(pattern, limit=5) returning words ranked as suggest, matching the
ENTIRE pattern: '?' matches one character, '*' zero or more, backslash escapes
the next character; dangling escape raises ValueError even for an empty catalog.
Consecutive stars allowed. Negative limit raises ValueError. Match Unicode by
Python character. Do not enumerate wildcard expansions.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
