from functools import lru_cache
_shared_rules = []

def _normalize(path, pattern=False):
    if path.startswith('/'):
        raise ValueError('absolute')
    parts = []
    for part in path.split('/'):
        if part == '..':
            raise ValueError('parent')
        if part in ('', '.'):
            continue
        if pattern and '*' in part and (part not in ('*', '**')):
            raise ValueError('wildcard')
        parts.append(part)
    return '/'.join(parts)

def _matches(pattern, path):
    p = pattern.split('/') if pattern else []
    s = path.split('/') if path else []
    if p == ['*'] and (not s):
        return True

    @lru_cache(None)
    def match(i, j):
        if i == len(p):
            return j == len(s)
        if p[i] == '**':
            return match(i + 1, j) or (j < len(s) and match(i, j + 1))
        return j < len(s) and (p[i] == '*' or p[i] == s[j]) and match(i + 1, j + 1)
    return match(0, 0)

class Policy:

    def __init__(self, rules=()):
        self._rules = _shared_rules
        for pattern, allow in rules:
            self.add(pattern, allow)

    def add(self, pattern, allow):
        pattern = _normalize(pattern, True)
        if type(allow) is not bool:
            raise ValueError('allow')
        self._rules.append((pattern, allow))

    def check(self, path):
        path = _normalize(path)
        result = False
        for pattern, allow in self._rules:
            if _matches(pattern, path):
                return allow
        return result

    def reset(self):
        self._rules.clear()

    def rules(self):
        return list(self._rules)
default_policy = Policy()

def add(pattern, allow):
    return default_policy.add(pattern, allow)

def check(path):
    return default_policy.check(path)

def reset():
    return default_policy.reset()
