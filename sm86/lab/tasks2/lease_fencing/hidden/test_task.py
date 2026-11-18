import pytest
from copy import deepcopy
from task import *

def test_case_00():
    c = Coordinator(lambda: 0)
    t = c.acquire('x', 'a', 5)
    assert t == 1
    assert c.acquire('x', 'b', 5) is None
    assert c.write('x', t, 7) and c.read('x') == 7


def test_case_01():
    now = [0]
    c = Coordinator(lambda: now[0])
    t = c.acquire('x', 'a', 5)
    now[0] = 5
    assert not c.write('x', t, 1)
    assert c.acquire('x', 'a', 2) == 2


def test_case_02():
    c = Coordinator(lambda: 0)
    t = c.acquire('x', 'a', 2)
    assert c.release('x', 'a', t)
    assert not c.release('x', 'a', t)


def test_case_03():
    now = [0]
    c = Coordinator(lambda: now[0])
    t = c.acquire('x', 'a', 2)
    now[0] = 1
    assert c.acquire('x', 'a', 5) == t
    now[0] = 5
    assert c.renew('x', 'a', t, 2)
    now[0] = 7
    assert not c.renew('x', 'a', t, 2)


def test_case_04():
    c = Coordinator(lambda: 0)
    a = c.acquire('a', 'o', 2)
    b = c.acquire('b', 'o', 2)
    assert (a, b) == (1, 2)
    assert not c.write('b', a, 3)


def test_case_05():
    c = Coordinator(lambda: 0)
    t = c.acquire('x', 'a', 2)
    assert not c.write_many([('x', t, 3), ('missing', 1, 4)])
    assert c.read('x') is None
    with pytest.raises(ValueError): c.write_many([('x', t, 1), ('x', t, 2)])


def test_case_06():
    c = Coordinator(lambda: 0)
    t = c.acquire('x', 'a', 2)
    v = [1]
    assert c.write('x', t, v)
    v.append(2)
    w = c.read('x')
    w.append(3)
    c.release('x', 'a', t)
    assert c.read('x') == [1]
    default = []
    assert c.read('absent', default) is default


def test_case_07():
    c = Coordinator(lambda: 0)
    for ttl in [0, -1]:
        with pytest.raises(ValueError): c.acquire('x', 'a', ttl)
        with pytest.raises(ValueError): c.renew('x', 'a', 1, ttl)
    assert not c.release('x', 'a', 1)
    assert c.write_many([])


def test_case_08():
    calls = [0]
    def clk():
        calls[0] += 1
        return calls[0]
    c = Coordinator(clk)
    a = c.acquire('a', 'o', 10)
    b = c.acquire('b', 'o', 10)
    before = calls[0]
    assert c.write_many(iter([('a', a, 1), ('b', b, 2)]))
    assert calls[0] == before + 1
    assert c.read('a') == 1 and c.read('b') == 2
