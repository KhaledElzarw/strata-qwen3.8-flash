import pytest
from copy import deepcopy
from task import *

def test_case_00():
    p = Priority()
    p.put('a', 2, 1)
    p.put('b', 1, 2)
    assert p.pop() == ('b', 2)


def test_case_01():
    p = Priority()
    p.put('a', 1, 2)
    assert p.peek() == ('a', 2) and len(p) == 1


def test_case_02():
    p = Priority()
    p.put('a', 1, 2)
    assert p.remove('a')
    assert not p.remove('a')


def test_case_03():
    p = Priority()
    p.put('a', 1, 'old')
    p.put('b', 1, 'b')
    p.put('a', 1, 'new')
    assert p.pop() == ('a', 'new')


def test_case_04():
    p = Priority()
    p.put('a', 0, 'old')
    p.put('a', 10, 'new')
    p.put('b', 5, 'b')
    assert p.pop() == ('b', 'b')
    assert p.pop() == ('a', 'new')


def test_case_05():
    p = Priority()
    p.put('a', 1, 1)
    p.put('b', 1, 2)
    p.remove('a')
    p.put('a', 1, 3)
    assert p.pop() == ('b', 2)


def test_case_06():
    p = Priority()
    p.put(None, 1, {})
    p.put(2, 1, [])
    assert p.pop() == (None, {})
    assert p.pop() == (2, [])


def test_case_07():
    p = Priority()
    p.put('a', 0, 1)
    p.put('a', 1, 2)
    p.remove('a')
    with pytest.raises(KeyError): p.peek()
    with pytest.raises(KeyError): p.pop()
    assert len(p) == 0


def test_case_08():
    p = Priority()
    for i in range(30): p.put('x', 30-i, i)
    assert p.pop() == ('x', 29)
    with pytest.raises(KeyError): p.pop()
    assert len(Priority()) == 0
