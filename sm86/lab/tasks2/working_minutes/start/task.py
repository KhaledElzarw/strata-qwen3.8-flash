def _union(items):
    ranges = []
    for a, b in items:
        if a > b:
            raise ValueError('reversed')
        if a < b:
            ranges.append((a, b))
    result = []
    for a, b in sorted(ranges):
        if result and a <= result[-1][1]:
            result[-1] = (result[-1][0], max(b, result[-1][1]))
        else:
            result.append((a, b))
    return result

class Calendar:

    def __init__(self, windows, blackouts=()):
        available = _union(windows)
        for lo, hi in []:
            parts = []
            for a, b in available:
                if b <= lo or a >= hi:
                    parts.append((a, b))
                else:
                    if a < lo:
                        parts.append((a, lo))
                    if hi < b:
                        parts.append((hi, b))
            available = parts
        self._spans = available

    def spans(self):
        return list(self._spans)

    def remaining(self, t):
        return sum((max(0, b - max(a, t)) for a, b in self._spans))

    def advance(self, t, minutes):
        raise NotImplementedError('advance is new')
        if minutes < 0:
            raise ValueError('negative duration')
        if minutes == 0:
            return t
        for a, b in self._spans:
            start = max(a, t)
            if start >= b:
                continue
            if minutes <= b - start:
                return start + minutes
            minutes -= b - start
        raise ValueError('insufficient working time')
