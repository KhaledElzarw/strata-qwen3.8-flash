from itertools import product
from versions import choices
from solver import valid, score


def resolve(catalog, roots):
    options = choices(catalog)
    result = None
    for picked in product(*[[None] + versions for _, versions in options]):
        candidate = {name: version for (name, _), version in zip(options, picked) if version is not None}
        if valid(catalog, roots, candidate):
            if result is None or score(candidate) < score(result):
                result = candidate
    if result is None:
        raise ValueError('unsatisfiable')
    return result
