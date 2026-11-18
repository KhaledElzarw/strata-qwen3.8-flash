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


def test_case_04():
    b = Bus()
    f = lambda x: b.emit('x', x)
    b.once('x', f)
    assert b.emit('x', 1) == [[]]


def test_case_05():
    b = Bus()
    def bad(x): raise RuntimeError('stop')
    b.once('x', bad)
    b.subscribe('x', lambda x: 4)
    with pytest.raises(RuntimeError): b.emit('x', 0)
    assert b.emit('x', 0) == [4]


def test_case_06():
    b = Bus()
    f = lambda x: 1
    b.once('x', f)
    assert not b.subscribe('x', f)
    b.emit('x', 0)
    assert b.emit('x', 0) == []


def test_case_07():
    f = lambda x: x
    assert subscribe('legacy', f)
    assert default_bus.emit('legacy', 3) == [3]
    assert emit('legacy', 4) == [4]
    assert unsubscribe('legacy', f)
    assert Bus().emit('legacy', 1) == []


def test_case_08():
    b = Bus()
    g = lambda x: 'g'
    def f(x):
        b.subscribe('x', g)
        return 'f'
    b.subscribe('x', f)
    assert b.emit('x', 0) == ['f']
    assert b.emit('x', 0) == ['f', 'g']


def test_case_09():
    b = Bus()
    f = lambda v: v
    b.subscribe('x', f)
    r = b.subscribers('x')
    r.clear()
    assert b.subscribers('x') == [f]
    assert b.clear('x') == 1
    assert b.clear('x') == 0


def test_case_10():
    b = Bus()
    b.subscribe('x', lambda v: v)
    b.subscribe('y', lambda v: v)
    assert b.clear() == 2
    assert b.subscribers('y') == []


def test_case_11():
    f = lambda v: v
    subscribe('clear-legacy', f)
    assert subscribers('clear-legacy') == [f]
    assert clear('clear-legacy') == 1
