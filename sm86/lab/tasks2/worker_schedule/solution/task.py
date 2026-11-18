import heapq

def schedule(jobs, workers):
    if workers <= 0:
        raise ValueError('workers')
    deps = {j: set(v[1]) for j, v in jobs.items()}
    for j, (duration, _) in jobs.items():
        if duration <= 0:
            raise ValueError('duration')
        for parent in deps[j]:
            if parent not in jobs:
                raise KeyError(parent)
    children = {j: [] for j in jobs}
    left = {j: len(d) for j, d in deps.items()}
    for j, parents in deps.items():
        for parent in parents:
            children[parent].append(j)
    ready = [j for j in jobs if not left[j]]
    heapq.heapify(ready)
    free = list(range(workers))
    running, result = ([], [])
    now = 0
    while ready or running:
        while ready and free:
            job = heapq.heappop(ready)
            worker = heapq.heappop(free)
            end = now + jobs[job][0]
            result.append((job, worker, now, end))
            heapq.heappush(running, (end, worker, job))
        if not running:
            break
        now = running[0][0]
        while running and running[0][0] == now:
            _, worker, job = heapq.heappop(running)
            heapq.heappush(free, worker)
            for child in children[job]:
                left[child] -= 1
                if left[child] == 0:
                    heapq.heappush(ready, child)
    if len(result) != len(jobs):
        raise ValueError('cycle')
    return sorted(result, key=lambda r: (r[2], r[1], r[0]))
