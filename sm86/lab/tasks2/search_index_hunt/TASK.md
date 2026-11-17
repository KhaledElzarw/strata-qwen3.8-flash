# Search index bug hunt
Repair task.py, words.py and postings.py. `Index.put(id, text)` inserts or
replaces a document. Tokenization is runs of Unicode alphabetic characters,
casefolded; digits, underscores and punctuation separate tokens. `remove(id)`
returns bool. `search(query)` ANDs the distinct query tokens: return document IDs
containing every token, sorted by decreasing total occurrence count of those
DISTINCT tokens, then lexical ID. Empty query tokens yield []. Replacing or
removing a document erases ALL its old postings, including terms still present
in others. Repeated query terms do not increase rank. IDs are strings, text/query
strings. `terms(id)` returns a fresh dict token -> count; missing raises KeyError.
Instances share nothing. Keep the public API and input data unchanged.

Run `python -m pytest -q` in this folder to check your work, and keep going until every test passes. Do not change anything under `tests/`. Use only the Python standard library.
