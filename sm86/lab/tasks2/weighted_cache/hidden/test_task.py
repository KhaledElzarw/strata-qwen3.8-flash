import pytest
from copy import deepcopy
from task import *

def test_case_00():
    c = Cache(3, lambda: 0)
    c.put('a', 1, 2)
    c.put('b', 2)
    assert c.weight == 3 and c.keys() == ['a', 'b']


def test_case_01():
    c = Cache(2, lambda: 0)
    c.put('a', 1)
    c.put('b', 2)
    c.get('a')
    c.put('c', 3)
    assert c.keys() == ['a', 'c']


def test_case_02():
    t = [0]
    c = Cache(2, lambda: t[0])
    c.put('a', 1, ttl=2)
    t[0] = 2
    assert c.get('a', 9) == 9


def test_case_03():
    c = Cache(2, lambda: 0)
    c.put('a', 1)
    c.put('b', 2)
    assert 'a' in c
    c.put('c', 3)
    assert c.keys() == ['b', 'c']


def test_case_04():
    c = Cache(2, lambda: 0)
    c.put('a', 1)
    c.put('a', 2, 3)
    assert c.keys() == []
    c.put('b', 2, ttl=0)
    assert c.weight == 0


def test_case_05():
    t = [0]
    c = Cache(3, lambda: t[0])
    c.put('old', 0, ttl=2)
    c.put('live', 1)
    t[0] = 2
    c.put('new', 2, 2)
    assert c.keys() == ['live', 'new']


def test_case_06():
    with pytest.raises(ValueError): Cache(0, lambda: 0)
    c = Cache(2, lambda: 0)
    c.put('a', 1)
    for kw in [{'weight': 0}, {'ttl': -1}]:
        with pytest.raises(ValueError): c.put('a', 2, **kw)
    assert c.get('a') == 1


def test_case_07():
    t = [0]
    c = Cache(2, lambda: t[0])
    c.put('a', 1, ttl=3)
    t[0] = 2
    c.get('a')
    t[0] = 3
    assert c.weight == 0


def test_case_08():
    calls = []
    def clock():
        calls.append(1)
        return 0
    c = Cache(2, clock)
    c.put('a', None)
    assert c.get('a', 9) is None
    assert c.keys() == ['a']
    assert len(calls) == 3


def test_case_09():
    c = Cache(5, lambda: 0)
    c.put('a', 1, 2)
    c.put('b', 2, 2)
    c.resize(2)
    assert c.keys() == ['b'] and c.weight == 2


def test_case_10():
    c = Cache(2, lambda: 0)
    c.put('a', 1)
    with pytest.raises(ValueError): c.resize(0)
    assert c.keys() == ['a']
    c.resize(4)
    assert c.keys() == ['a']


def test_case_11():
    t = [0]
    c = Cache(3, lambda: t[0])
    c.put('a', 1, 2, ttl=1)
    c.put('b', 2)
    t[0] = 1
    c.resize(1)
    assert c.keys() == ['b']
