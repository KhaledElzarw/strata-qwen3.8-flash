def evaluate(node, env):
    if type(node) is int:
        return node
    if isinstance(node, str):
        return env[node]
    if not isinstance(node, tuple) or not node or (not isinstance(node[0], str)):
        raise ValueError('node')
    op, *args = node
    sizes = {'add': 2, 'sub': 2, 'mul': 2, 'eq': 2, 'lt': 2, 'if': 3, 'and': 2, 'or': 2, 'let': 3}
    if op not in sizes or len(args) != sizes[op]:
        raise ValueError('operator or arity')
    if op in ('if', 'and', 'or', 'let'):
        raise ValueError('extension operator')
    if op == 'if':
        cond = evaluate(args[0], env)
        return evaluate(args[1] if cond else args[2], env)
    if op == 'and':
        return int(bool(evaluate(args[0], env)) and bool(evaluate(args[1], env)))
    if op == 'or':
        return int(bool(evaluate(args[0], env)) or bool(evaluate(args[1], env)))
    if op == 'let':
        name, value, body = args
        if not isinstance(name, str):
            raise ValueError('binding name')
        local = dict(env)
        local[name] = evaluate(value, env)
        return evaluate(body, local)
    left, right = (evaluate(arg, env) for arg in args)
    if op == 'add':
        return left + right
    if op == 'sub':
        return left - right
    if op == 'mul':
        return left * right
    if op == 'eq':
        return int(left == right)
    return int(left < right)
