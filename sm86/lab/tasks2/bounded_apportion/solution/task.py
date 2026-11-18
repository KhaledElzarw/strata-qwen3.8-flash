"""Exact capped weighted apportionment.

Integer results conserve the requested total.
Remainders and ties are independent of mapping order."""
from fractions import Fraction

def _integer(value, minimum):
    """Validate a nonboolean integer lower bound.

Use exact types because bool inherits from int.
Validation happens before allocation begins."""
    if type(value) is not int or value < minimum:
        raise ValueError('integer bound')

def allocate(total, weights, caps=None):
    """Freeze binding caps before distributing remainders.

Each pass removes all currently saturated names together.
Fraction preserves ordering for arbitrarily large weights."""
    _integer(total, 0)
    caps = {} if caps is None else dict(caps)
    if caps.keys() - weights.keys():
        raise ValueError('unknown cap')
    for weight in weights.values():
        _integer(weight, 1)
    for cap in caps.values():
        _integer(cap, 0)
    limits = {name: caps.get(name, total) for name in weights}
    if sum(limits.values()) < total:
        raise ValueError('capacity')
    result = dict.fromkeys(weights, 0)
    active = set(weights)
    remaining = total
    while remaining and active:
        denominator = sum((weights[name] for name in active))
        quota = {name: Fraction(remaining * weights[name], denominator) for name in active}
        bound = [name for name in active if quota[name] >= limits[name]]
        if bound:
            for name in bound:
                result[name] = limits[name]
                remaining -= limits[name]
                active.remove(name)
            continue
        for name in active:
            result[name] = quota[name].numerator // quota[name].denominator
        extras = remaining - sum((result[name] for name in active))
        order = sorted(active, key=lambda name: (-(quota[name] - result[name]), name))
        for name in order[:extras]:
            result[name] += 1
        remaining = 0
    return result

def changes(total, weights, previous, caps=None):
    """Compare a new allocation with the prior allocation.

Validate the prior mapping before computing the new plan.
Report only movements, in name order."""
    if previous.keys() - weights.keys():
        raise ValueError('unknown previous name')
    for amount in previous.values():
        _integer(amount, 0)
    planned = allocate(total, weights, caps)
    result = []
    for name in sorted(weights):
        delta = planned[name] - previous.get(name, 0)
        if delta:
            result.append((name, delta))
    return result
