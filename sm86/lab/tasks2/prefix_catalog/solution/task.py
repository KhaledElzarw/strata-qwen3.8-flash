from functools import lru_cache

class Catalog:

    def __init__(self):
        self.words = {}

    def put(self, word, weight):
        if not isinstance(word, str) or not word or type(weight) is not int or (weight < 0):
            raise ValueError('word or weight')
        self.words[word] = weight

    def remove(self, word):
        if word not in self.words:
            return False
        del self.words[word]
        return True

    def suggest(self, prefix='', limit=5):
        if limit < 0:
            raise ValueError('limit')
        matching = (w for w in self.words if w.startswith(prefix))
        return sorted(matching, key=lambda w: (-self.words[w], w))[:limit]

    def prefix_weight(self, prefix):
        return sum((v for w, v in self.words.items() if w.startswith(prefix)))

    def longest(self, text):
        matching = [w for w in self.words if text.startswith(w)]
        return max(matching, key=len) if matching else None

    def __len__(self):
        return len(self.words)

    def match(self, pattern, limit=5):
        if limit < 0:
            raise ValueError('limit')
        tokens = []
        i = 0
        while i < len(pattern):
            ch = pattern[i]
            if ch == '\\':
                i += 1
                if i == len(pattern):
                    raise ValueError('escape')
                tokens.append(('literal', pattern[i]))
            else:
                tokens.append((ch if ch in '*?' else 'literal', ch))
            i += 1

        def accepts(word):

            @lru_cache(None)
            def visit(i, j):
                if i == len(tokens):
                    return j == len(word)
                kind, value = tokens[i]
                if kind == '*':
                    return visit(i + 1, j) or (j < len(word) and visit(i, j + 1))
                return j < len(word) and (kind == '?' or value == word[j]) and visit(i + 1, j + 1)
            return visit(0, 0)
        return [w for w in self.suggest('', len(self)) if accepts(w)][:limit]
