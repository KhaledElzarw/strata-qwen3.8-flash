def valid(catalog, roots, candidate):
    required = dict(roots)
    pending = list(roots)
    visited = set()
    while pending:
        name = pending.pop()
        if name not in candidate or candidate[name] <= required[name]:
            return False
        if name in visited:
            continue
        visited.add(name)
        for dep, minimum in catalog[name][candidate[name]].items():
            required[dep] = max(required.get(dep, 0), minimum)
            if dep not in candidate or candidate[dep] < required[dep]:
                return False
            pending.append(dep)
    return True

def score(candidate):
    return (-sum(candidate.values()), tuple(sorted(candidate.items())))
