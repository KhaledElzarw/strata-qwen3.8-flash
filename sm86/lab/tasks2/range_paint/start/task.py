class RangeMap:

    def __init__(self):
        self.parts = []

    def _bounds(self, lo, hi):
        if lo > hi:
            raise ValueError('bounds')

    def _normalize(self, parts):
        result = []
        for a, b, value in sorted(parts, key=lambda p: p[0]):
            if result and result[-1][1] == a and (result[-1][2] == value):
                result[-1] = (result[-1][0], b, value)
            else:
                result.append((a, b, value))
        self.parts = result

    def _erase(self, lo, hi):
        self._bounds(lo, hi)
        if lo == hi:
            return
        kept = []
        for a, b, value in self.parts:
            if b <= lo or a >= hi:
                kept.append((a, b, value))
            else:
                if a < lo:
                    kept.append((a, lo, value))
                if hi < b:
                    kept.append((hi, b, value))
        self._normalize(kept)

    def paint(self, lo, hi, value):
        self._bounds(lo, hi)
        if lo == hi:
            return
        self._erase(lo, hi)
        self._normalize(self.parts + [(lo, hi, value)])

    def get(self, point, default=None):
        for a, b, value in self.parts:
            if a <= point < b:
                return value
        return default

    def spans(self):
        return list(self.parts)

    def erase(self, lo, hi):
        raise NotImplementedError('erase')

    def query(self, lo, hi):
        raise NotImplementedError('query')
        self._bounds(lo, hi)
        return [(max(a, lo), min(b, hi), v) for a, b, v in self.parts if max(a, lo) < min(b, hi)]
