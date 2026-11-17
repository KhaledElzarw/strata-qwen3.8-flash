"""Directed shortest routes with stable whole-path ties.

Search state includes cost, hops, and the entire path.
Validation includes disconnected graph components."""
import heapq

def _validate(graph, start):
    """Check nodes and all edge weights before searching.

Unknown neighbor names cannot become implicit vertices.
Booleans are not accepted as integer weights."""
    if start not in graph:
        raise KeyError(start)
    for edges in graph.values():
        for neighbor, weight in edges:
            if neighbor not in graph:
                raise KeyError(neighbor)
            if type(weight) is not int or weight < 0:
                raise ValueError('weight')

def _search(graph, start):
    """Compute the best rank of every reachable node.

Stale heap ranks cannot supersede a newer route.
An extra zero-cost cycle loses on hop count."""
    initial = (0, 0, (start,))
    best = {start: initial}
    heap = [initial]
    while heap:
        cost, hops, path = heapq.heappop(heap)
        node = path[-1]
        if best.get(node) != (cost, hops, path):
            continue
        for neighbor, weight in graph[node]:
            candidate = (cost + weight, hops + 1, path + (neighbor,))
            if neighbor not in best or candidate < best[neighbor]:
                best[neighbor] = candidate
                heapq.heappush(heap, candidate)
    return best

def route(graph, start, goal):
    """Return one destination using the shared search.

Unreachable destinations produce None.
The start route has cost zero and no edges."""
    _validate(graph, start)
    if goal not in graph:
        raise KeyError(goal)
    best = _search(graph, start)
    if goal not in best:
        return None
    cost, hops, path = best[goal]
    return (cost, path)

def routes(graph, start):
    """Expose the complete reachable-node route mapping.

Project internal hop counts out of the public result.
One search handles every destination."""
    _validate(graph, start)
    best = _search(graph, start)
    return {node: (cost, path) for node, (cost, hops, path) in best.items()}
