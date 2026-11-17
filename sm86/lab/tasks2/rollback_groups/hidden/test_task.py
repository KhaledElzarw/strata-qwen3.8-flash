import pytest
from copy import deepcopy
from task import *

def test_case_00():
    g = Groups('abc')
    assert g.union('a', 'b')
    assert g.connected('a', 'b')
    assert g.size('a') == 2 and g.count == 2


def test_case_01():
    g = Groups('abc')
    m = g.snapshot()
    g.union('a', 'b')
    g.rollback(m)
    assert not g.connected('a', 'b')


def test_case_02():
    g = Groups('ab')
    assert g.union('a', 'b')
    assert not g.union('b', 'a')
    assert g.snapshot() == 1


def test_case_03():
    g = Groups('abcd')
    g.union('a', 'b')
    m = g.snapshot()
    g.union('c', 'd')
    g.union('b', 'd')
    g.rollback(m)
    assert g.members('a') == frozenset('ab')
    assert g.size('c') == 1


def test_case_04():
    g = Groups(['z', 'a', 'b', 'c'])
    g.union('a', 'z')
    g.union('c', 'b')
    g.union('c', 'a')
    assert g.representative('c') == 'z'


def test_case_05():
    g = Groups('abc')
    g.union('a', 'b')
    g.rollback(0)
    g.union('b', 'c')
    g.rollback(1)
    assert g.members('b') == frozenset('bc')


def test_case_06():
    g = Groups('a')
    for m in [-1, 1, True, 0.0]:
        with pytest.raises(ValueError): g.rollback(m)
    with pytest.raises(KeyError): g.union('a', 'x')
    assert g.snapshot() == 0


def test_case_07():
    with pytest.raises(ValueError): Groups(['a', 'a'])
    g = Groups([])
    assert g.count == 0
    g.rollback(0)


def test_case_08():
    g = Groups(range(1000))
    for i in range(1, 1000): g.union(i-1, i)
    assert g.size(999) == 1000 and g.representative(999) == 0
    g.rollback(500)
    assert g.size(0) == 501 and g.count == 500
