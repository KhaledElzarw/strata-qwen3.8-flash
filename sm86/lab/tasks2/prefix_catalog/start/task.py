from functools import lru_cache

class Catalog:

    def __init__(self):
        raise NotImplementedError()

    def put(self, word, weight):
        raise NotImplementedError()

    def remove(self, word):
        raise NotImplementedError()

    def suggest(self, prefix='', limit=5):
        raise NotImplementedError()

    def prefix_weight(self, prefix):
        raise NotImplementedError()

    def longest(self, text):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def match(self, pattern, limit=5):
        raise NotImplementedError()
