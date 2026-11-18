import pytest
from copy import deepcopy
from task import *

def test_case_00():
    b = Bus()
    f = lambda x: x+1
    assert b.subscribe('x', f)
    assert b.emit('x', 3) == [4]


def test_case_01():
    b = Bus()
    f = lambda x: x
    assert b.subscribe('x', f)
    assert not b.subscribe('x', f)
    assert b.unsubscribe('x', f)


def test_case_02():
    b = Bus()
    b.once('x', lambda v: v)
    assert b.emit('x', 1) == [1]
    assert b.emit('x', 2) == []


def test_case_03():
    b = Bus()
    seen = []
    def f(x):
        b.unsubscribe('x', g)
        return 'f'
    def g(x): return 'g'
    b.subscribe('x', f)
    b.subscribe('x', g)
    assert b.emit('x', 0) == ['f', 'g']
    assert b.emit('x', 0) == ['f']
