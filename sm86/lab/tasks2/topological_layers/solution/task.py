def layers(graph):
    deps = {node: set(parents) for node, parents in graph.items()}
    for parents in deps.values():
        for parent in parents:
            if parent not in graph:
                raise KeyError(parent)
    pending = set(graph)
    done = set()
    rounds = []
    while pending:
        ready = sorted((node for node in pending if deps[node] <= done))
        if not ready:
            break
        rounds.append(ready)
        done.update(ready)
        pending.difference_update(ready)
    return (rounds, sorted(pending))

def order(graph):
    rounds, blocked = layers(graph)
    if blocked:
        raise ValueError(tuple(blocked))
    return [node for group in rounds for node in group]
