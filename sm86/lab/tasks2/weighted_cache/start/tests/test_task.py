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
