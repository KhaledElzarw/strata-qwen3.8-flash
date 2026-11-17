from common import emit

emit('ranked_routes', 'graphs', 2, 'implement', '''
# Deterministic shortest routes
Implement `route(graph, start, goal)`. graph maps string nodes to lists of
`(neighbor, weight)` directed edges; every neighbor must be a graph key, else
KeyError. All weights must be nonnegative integers (bool invalid), else ValueError.
Validate ALL edges, including unreachable ones. Missing start/goal raises
KeyError. Return `(cost, path)` with path a tuple including both endpoints, or
None when unreachable. Minimize cost, then number of edges, then full path
lexicographically. Parallel edges and self loops are allowed. start==goal returns
(0,(start,)) after validation. Do not mutate graph. Support at least 300 nodes;
use a shortest-path algorithm, not enumeration of all paths. Zero-cost cycles
must terminate and never improve an equal-cost route with extra hops.
''', '''
import heapq


def route(graph, start, goal):
    if start not in graph: raise KeyError(start)
    if goal not in graph: raise KeyError(goal)
    for edges in graph.values():
        for neighbor, weight in edges:
            if neighbor not in graph: raise KeyError(neighbor)
            if type(weight) is not int or weight < 0: raise ValueError('weight')
    initial = (0, 0, (start,))
    best = {start: initial}
    heap = [initial]
    while heap:
        cost, hops, path = heapq.heappop(heap)
        node = path[-1]
        if best.get(node) != (cost, hops, path): continue
        if node == goal: return cost, path
        for neighbor, weight in graph[node]:
            candidate = cost + weight, hops + 1, path + (neighbor,)
            if neighbor not in best or candidate < best[neighbor]:
                best[neighbor] = candidate
                heapq.heappush(heap, candidate)
    return None
''', [
"assert route({'a': [('b', 2)], 'b': []}, 'a', 'b') == (2, ('a', 'b'))",
"assert route({'a': [], 'b': []}, 'a', 'b') is None",
"assert route({'a': []}, 'a', 'a') == (0, ('a',))",
"g = {'s': [('a', 1), ('t', 2)], 'a': [('t', 1)], 't': []}\nassert route(g, 's', 't') == (2, ('s', 't'))",
"g = {'s': [('b', 1), ('a', 1)], 'a': [('t', 1)], 'b': [('t', 1)], 't': []}\nassert route(g, 's', 't') == (2, ('s', 'a', 't'))",
"g = {'s': [('s', 0), ('a', 0)], 'a': [('s', 0), ('t', 1)], 't': []}\nassert route(g, 's', 't') == (1, ('s', 'a', 't'))",
"for g in [{'a': [], 'z': [('x', 1)]}, {'a': [], 'z': [('a', -1)]}, {'a': [('a', True)]}]:\n    with pytest.raises((KeyError, ValueError)): route(g, 'a', 'a')\nwith pytest.raises(KeyError): route({}, 'a', 'b')",
"g = {'a': [('b', 9), ('b', 2)], 'b': []}\nold = deepcopy(g)\nassert route(g, 'a', 'b')[0] == 2\nassert g == old",
"g = {str(i): [(str(i+1), 1)] if i < 299 else [] for i in range(300)}\nr = route(g, '0', '299')\nassert r[0] == 299 and len(r[1]) == 300",
])

emit('topological_layers', 'graphs', 3, 'fix', '''
# Repair dependency layers and blocked nodes
Fix `layers(graph)` for dict node -> iterable of prerequisite string nodes.
Prerequisites must exist, else KeyError. Duplicates count once; inputs unchanged.
Return `(rounds, blocked)`: rounds is a list of sorted lists. In each round emit
ALL nodes whose prerequisites were completed in EARLIER rounds, never same round.
Continue until none are ready. blocked is sorted nodes left, including both
cycle members and acyclic nodes depending on a cycle. Empty graph gives ([], []).
A self dependency blocks itself. Distinct insertion orders yield identical
results. Handle disconnected graphs and at least 500 nodes. Do not raise for
cycles. Implement `order(graph)` flattening rounds; if any blocked nodes exist,
raise ValueError whose first argument is tuple(blocked), with no partial order.
''', '''
def layers(graph):
    deps = {node: set(parents) for node, parents in graph.items()}
    for parents in deps.values():
        for parent in parents:
            if parent not in graph: raise KeyError(parent)
    pending = set(graph)
    done = set()
    rounds = []
    while pending:
        ready = sorted(node for node in pending if deps[node] <= done)
        if not ready: break
        rounds.append(ready)
        done.update(ready)
        pending.difference_update(ready)
    return rounds, sorted(pending)


def order(graph):
    rounds, blocked = layers(graph)
    if blocked: raise ValueError(tuple(blocked))
    return [node for group in rounds for node in group]
''', [
"assert layers({'a': [], 'b': ['a']}) == ([['a'], ['b']], [])",
"assert order({'b': [], 'a': []}) == ['a', 'b']",
"assert layers({}) == ([], [])",
"g = {'a': ['b'], 'b': ['a'], 'c': ['b'], 'z': []}\nassert layers(g) == ([['z']], ['a', 'b', 'c'])",
"assert layers({'a': [], 'b': ['a', 'a']}) == ([['a'], ['b']], [])",
"with pytest.raises(KeyError): layers({'a': ['x']})\nwith pytest.raises(ValueError) as e: order({'a': ['a']})\nassert e.value.args == (('a',),)",
"g = {'c': ['b'], 'b': ['a'], 'a': []}\nassert layers(g) == ([['a'], ['b'], ['c']], [])",
"g = {'c': ['a'], 'a': [], 'b': []}\nold = deepcopy(g)\nassert order(g) == ['a', 'b', 'c']\nassert g == old",
"g = {f'n{i:03}': [] if i == 0 else [f'n{i-1:03}'] for i in range(500)}\nassert len(layers(g)[0]) == 500",
], start=[('task.py', 'deps[node] <= done', 'not deps[node] or any(parent in done for parent in deps[node])'), ('task.py', 'return rounds, sorted(pending)', "return rounds, sorted(node for node in pending if node in deps[node] or any(node in deps[p] for p in deps[node]))")])

emit('component_condensation', 'graphs', 4, 'extend', '''
# Strong components with condensation and reachability
Extend `components(graph)` and add `condense(graph)` and `reachable(graph, node)`.
graph maps string nodes to iterable outgoing neighbors; duplicates ignored.
Unknown neighbors or queried node raise KeyError. No input mutation.
components returns strongly connected components as sorted tuples, with the
list sorted lexicographically by tuple. Support >=1200 nodes in a chain without
hitting Python recursion limits. condense returns `(groups, edges)` where groups
is components' result, each component ID its list index, edges sorted unique
`(source_id, target_id)` pairs, excluding within-component edges. reachable
returns sorted nodes reachable by any directed path INCLUDING the starting node.
Validate all graph edges even if unreachable from queried node. Empty graph
returns [] / ([], []). Accept one-shot neighbor iterables for each call.
Keep existing components results on small graphs; remove recursion-depth limits.
''', '''
def _read(graph):
    edges = {node: set(neighbors) for node, neighbors in graph.items()}
    for neighbors in edges.values():
        for target in neighbors:
            if target not in edges: raise KeyError(target)
    return edges


def _groups(edges):
    seen, finish = set(), []
    for root in sorted(edges):
        if root in seen: continue
        seen.add(root)
        stack = [(root, iter(sorted(edges[root])))]
        while stack:
            node, children = stack[-1]
            target = next(children, None)
            if target is None:
                finish.append(node)
                stack.pop()
            elif target not in seen:
                seen.add(target)
                stack.append((target, iter(sorted(edges[target]))))
    reverse = {node: set() for node in edges}
    for node, children in edges.items():
        for target in children: reverse[target].add(node)
    seen, groups = set(), []
    for root in reversed(finish):
        if root in seen: continue
        stack, group = [root], []
        seen.add(root)
        while stack:
            node = stack.pop()
            group.append(node)
            for target in reverse[node]:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
        groups.append(tuple(sorted(group)))
    return sorted(groups)


def components(graph):
    return _groups(_read(graph))


def condense(graph):
    edges = _read(graph)
    groups = _groups(edges)
    ids = {node: i for i, group in enumerate(groups) for node in group}
    links = {(ids[node], ids[target]) for node in edges for target in edges[node] if ids[node] != ids[target]}
    return groups, sorted(links)


def reachable(graph, node):
    edges = _read(graph)
    if node not in edges: raise KeyError(node)
    seen, stack = {node}, [node]
    while stack:
        for target in edges[stack.pop()]:
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return sorted(seen)
''', [
"assert components({'a': ['b'], 'b': ['a'], 'c': []}) == [('a', 'b'), ('c',)]",
"assert condense({'a': ['b'], 'b': ['a', 'c'], 'c': []}) == ([('a', 'b'), ('c',)], [(0, 1)])",
"assert reachable({'a': ['b'], 'b': [], 'c': []}, 'a') == ['a', 'b']",
"assert condense({'z': ['a', 'a', 'z'], 'a': []}) == ([('a',), ('z',)], [(1, 0)])",
"assert components({}) == []\nassert condense({}) == ([], [])\nassert reachable({'a': ['a']}, 'a') == ['a']",
"for fn in [components, condense, lambda g: reachable(g, 'a')]:\n    with pytest.raises(KeyError): fn({'a': [], 'z': ['missing']})\nwith pytest.raises(KeyError): reachable({}, 'x')",
"g = {'a': ['b'], 'b': ['c'], 'c': ['a', 'd'], 'd': ['e'], 'e': ['d']}\nassert components(g) == [('a', 'b', 'c'), ('d', 'e')]\nassert reachable(g, 'd') == ['d', 'e']",
"g = {str(i): [str(i+1)] if i < 1199 else [] for i in range(1200)}\nassert len(components(g)) == 1200\nassert len(reachable(g, '0')) == 1200",
"g = {'a': ['b'], 'b': []}\nold = deepcopy(g)\nassert condense(g)[1] == [(0, 1)]\nassert g == old\nassert components({'a': iter(['b']), 'b': iter(['a'])}) == [('a', 'b')]",
], start=[('task.py', 'def condense(graph):\n    edges', "def condense(graph):\n    raise NotImplementedError('condensation')\n    edges"), ('task.py', 'def reachable(graph, node):\n    edges', "def reachable(graph, node):\n    raise NotImplementedError('reachability')\n    edges")])

emit('assignment_matching', 'graphs', 4, 'implement', '''
# Maximum matching with cost and lexical ties
Implement `match(costs)` where costs maps worker string -> dict job string ->
integer cost; absent edges are forbidden. Each worker/job can be used at most
once. Return `(pairs, total_cost)` with pairs a sorted tuple of `(worker, job)`.
First maximize the number of pairs, then minimize total cost (negative costs
allowed), then choose the lexicographically smallest pairs tuple. Empty/isolated
workers are valid. Reject bool or noninteger costs with ValueError. Do not mutate
inputs. Handle up to 12 distinct jobs and 20 workers; enumerating all matchings
is too slow. Use subset dynamic programming or a polynomial matching algorithm.
Job IDs come from all inner keys; workers may remain unmatched. Empty input
returns `((), 0)`. Ties compare the whole sorted pairs sequence, not just jobs.
''', '''
def match(costs):
    jobs = sorted({job for edges in costs.values() for job in edges})
    ids = {job: i for i, job in enumerate(jobs)}
    for edges in costs.values():
        if any(type(cost) is not int for cost in edges.values()):
            raise ValueError('cost')
    best = {0: (0, ())}
    for worker in sorted(costs):
        next_best = dict(best)
        for mask, (total, pairs) in best.items():
            for job, cost in costs[worker].items():
                bit = 1 << ids[job]
                if mask & bit: continue
                new_mask = mask | bit
                candidate = total + cost, pairs + ((worker, job),)
                if new_mask not in next_best or candidate < next_best[new_mask]:
                    next_best[new_mask] = candidate
        best = next_best
    mask, (total, pairs) = min(best.items(), key=lambda item: (-item[0].bit_count(), item[1]))
    return pairs, total
''', [
"assert match({'a': {'x': 2}, 'b': {'y': 3}}) == ((('a', 'x'), ('b', 'y')), 5)",
"assert match({}) == ((), 0)",
"assert match({'a': {'x': 3}, 'b': {'x': 1}}) == ((('b', 'x'),), 1)",
"assert match({'a': {'x': 0, 'y': 100}, 'b': {'x': 0}}) == ((('a', 'y'), ('b', 'x')), 100)",
"assert match({'b': {'y': 1, 'x': 1}, 'a': {'y': 1, 'x': 1}}) == ((('a', 'x'), ('b', 'y')), 2)",
"assert match({'a': {'x': -5}, 'b': {'x': -5}, 'c': {}}) == ((('a', 'x'),), -5)",
"for value in [True, 1.0, '1']:\n    with pytest.raises(ValueError): match({'a': {'x': value}})",
"c = {'a': {'x': 2, 'y': 1}, 'b': {'x': 1, 'y': 2}}\nold = deepcopy(c)\nassert match(c) == ((('a', 'y'), ('b', 'x')), 2)\nassert c == old",
"c = {f'w{i:02}': {f'j{j:02}': abs(i-j) for j in range(12)} for i in range(20)}\npairs, cost = match(c)\nassert len(pairs) == 12 and cost == 0\nassert pairs == tuple((f'w{i:02}', f'j{i:02}') for i in range(12))",
])
