from bisect import bisect_right

def select(jobs, gap=0):
    if gap < 0:
        raise ValueError('gap')
    items = list(jobs)
    seen = set()
    for ident, start, end, reward in items:
        if ident in seen or start >= end:
            raise ValueError('job')
        seen.add(ident)
    items.sort(key=lambda j: (j[2], j[1], j[0]))
    ends = [j[2] for j in items]
    best = [(0, ())]
    for index, (ident, start, end, reward) in enumerate(items):
        previous = bisect_right(ends, start - gap, 0, index)
        total, ids = best[previous]
        take = (total + reward, ids + (ident,))
        skip = best[-1]
        best.append(min((take, skip), key=lambda x: (-x[0], len(x[1]), x[1])))
    return best[-1]
