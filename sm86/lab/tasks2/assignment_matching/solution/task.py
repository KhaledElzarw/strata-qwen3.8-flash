def match(costs):
    jobs = sorted({job for edges in costs.values() for job in edges})
    ids = {job: i for i, job in enumerate(jobs)}
    for edges in costs.values():
        if any((type(cost) is not int for cost in edges.values())):
            raise ValueError('cost')
    best = {0: (0, ())}
    for worker in sorted(costs):
        next_best = dict(best)
        for mask, (total, pairs) in best.items():
            for job, cost in costs[worker].items():
                bit = 1 << ids[job]
                if mask & bit:
                    continue
                new_mask = mask | bit
                candidate = (total + cost, pairs + ((worker, job),))
                if new_mask not in next_best or candidate < next_best[new_mask]:
                    next_best[new_mask] = candidate
        best = next_best
    mask, (total, pairs) = min(best.items(), key=lambda item: (-item[0].bit_count(), item[1]))
    return (pairs, total)
