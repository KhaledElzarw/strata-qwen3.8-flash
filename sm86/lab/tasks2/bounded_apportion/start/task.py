"""Exact capped weighted apportionment.

Integer results conserve the requested total.
Remainders and ties are independent of mapping order."""
from fractions import Fraction

def _integer(value, minimum):
    """Validate a nonboolean integer lower bound.

Use exact types because bool inherits from int.
Validation happens before allocation begins."""
    raise NotImplementedError()

def allocate(total, weights, caps=None):
    """Freeze binding caps before distributing remainders.

Each pass removes all currently saturated names together.
Fraction preserves ordering for arbitrarily large weights."""
    raise NotImplementedError()

def changes(total, weights, previous, caps=None):
    """Compare a new allocation with the prior allocation.

Validate the prior mapping before computing the new plan.
Report only movements, in name order."""
    raise NotImplementedError()
