def discard(postings, ident, terms):
    for term in terms:
        postings[term].pop(ident, None)
        if not postings[term]:
            del postings[term]

def rank(postings, words):
    words = set(words)
    if not words:
        return []
    groups = [set(postings.get(w, {})) for w in words]
    common = set.intersection(*groups)
    return sorted(common, key=lambda ident: (-sum((postings[w][ident] for w in words)), ident))
