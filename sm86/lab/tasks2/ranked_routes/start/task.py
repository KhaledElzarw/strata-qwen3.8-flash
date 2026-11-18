"""Directed shortest routes with stable whole-path ties.

Search state includes cost, hops, and the entire path.
Validation includes disconnected graph components."""
import heapq

def _validate(graph, start):
    """Check nodes and all edge weights before searching.

Unknown neighbor names cannot become implicit vertices.
Booleans are not accepted as integer weights."""
    raise NotImplementedError()

def _search(graph, start):
    """Compute the best rank of every reachable node.

Stale heap ranks cannot supersede a newer route.
An extra zero-cost cycle loses on hop count."""
    raise NotImplementedError()

def route(graph, start, goal):
    """Return one destination using the shared search.

Unreachable destinations produce None.
The start route has cost zero and no edges."""
    raise NotImplementedError()

def routes(graph, start):
    """Expose the complete reachable-node route mapping.

Project internal hop counts out of the public result.
One search handles every destination."""
    raise NotImplementedError()
