import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = RangeMap()
    r.paint(0, 5, 'a')
    assert r.get(2) == 'a'
    assert r.get(5, 'x') == 'x'


def test_case_01():
    r = RangeMap()
    r.paint(0, 5, 'a')
    r.erase(2, 3)
    assert r.spans() == [(0, 2, 'a'), (3, 5, 'a')]


def test_case_02():
    r = RangeMap()
    r.paint(0, 10, 'a')
    assert r.query(3, 6) == [(3, 6, 'a')]


def test_case_03():
    r = RangeMap()
    r.paint(0, 10, 'a')
    r.paint(3, 7, 'b')
    assert r.spans() == [(0, 3, 'a'), (3, 7, 'b'), (7, 10, 'a')]


def test_case_04():
    r = RangeMap()
    r.paint(0, 3, None)
    r.paint(3, 5, None)
    assert r.spans() == [(0, 5, None)]
    assert r.get(1, 'missing') is None


def test_case_05():
    r = RangeMap()
    r.paint(-10**12, 10**12, 'a')
    r.erase(-1, 1)
    assert r.query(-2, 2) == [(-2, -1, 'a'), (1, 2, 'a')]


def test_case_06():
    r = RangeMap()
    r.paint(0, 3, 'a')
    for f in [lambda: r.paint(2, 1, 'b'), lambda: r.erase(2, 1), lambda: r.query(2, 1)]:
        with pytest.raises(ValueError): f()
    assert r.spans() == [(0, 3, 'a')]


def test_case_07():
    r = RangeMap()
    r.paint(0, 2, 'a')
    r.erase(1, 1)
    r.paint(1, 1, 'b')
    assert r.query(1, 1) == []
    s = r.spans()
    s.clear()
    assert r.spans() == [(0, 2, 'a')]


def test_case_08():
    r = RangeMap()
    r.paint(0, 10, 'a')
    r.paint(2, 8, 'b')
    r.paint(2, 8, 'a')
    assert r.spans() == [(0, 10, 'a')]
    r.erase(-1, 11)
    assert r.spans() == []
