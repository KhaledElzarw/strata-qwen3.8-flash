from words import counts
from postings import discard, rank

class Index:

    def __init__(self):
        self.docs = {}
        self.postings = {}

    def put(self, ident, text):
        terms = counts(text)
        self.docs[ident] = terms
        for term, count in terms.items():
            self.postings.setdefault(term, {})[ident] = count

    def remove(self, ident):
        if ident not in self.docs:
            return False
        discard(self.postings, ident, self.docs.pop(ident))
        return True

    def search(self, query):
        return rank(self.postings, counts(query))

    def terms(self, ident):
        return dict(self.docs[ident])
