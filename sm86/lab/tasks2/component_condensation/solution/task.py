def _read(graph):
    edges = {node: set(neighbors) for node, neighbors in graph.items()}
    for neighbors in edges.values():
        for target in neighbors:
            if target not in edges:
                raise KeyError(target)
    return edges

def _groups(edges):
    seen, finish = (set(), [])
    for root in sorted(edges):
        if root in seen:
            continue
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
        for target in children:
            reverse[target].add(node)
    seen, groups = (set(), [])
    for root in reversed(finish):
        if root in seen:
            continue
        stack, group = ([root], [])
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
    return (groups, sorted(links))

def reachable(graph, node):
    edges = _read(graph)
    if node not in edges:
        raise KeyError(node)
    seen, stack = ({node}, [node])
    while stack:
        for target in edges[stack.pop()]:
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return sorted(seen)
