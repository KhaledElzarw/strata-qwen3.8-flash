import pytest
from copy import deepcopy
from task import *

def test_case_00():
    c = Calendar([(5, 10), (0, 5)])
    assert c.spans() == [(0, 10)]
    assert c.remaining(3) == 7


def test_case_01():
    assert Calendar([(0, 10)], [(3, 7)]).spans() == [(0, 3), (7, 10)]


def test_case_02():
    assert Calendar([(2, 5), (8, 12)]).advance(0, 5) == 10


def test_case_03():
    c = Calendar([(2, 5), (8, 12)])
    assert c.advance(2, 3) == 5
    assert c.advance(5, 1) == 9


def test_case_04():
    assert Calendar([]).advance(99, 0) == 99
    with pytest.raises(ValueError): Calendar([]).advance(0, 1)


def test_case_05():
    c = Calendar([(0, 10)], [(-3, 2), (4, 6), (5, 9), (10, 20)])
    assert c.spans() == [(2, 4), (9, 10)]
    assert c.remaining(3) == 2


def test_case_06():
    with pytest.raises(ValueError): Calendar([(2, 1)])
    with pytest.raises(ValueError): Calendar([], [(3, 2)])
    with pytest.raises(ValueError): Calendar([]).advance(0, -1)


def test_case_07():
    w = [[0, 10]]
    c = Calendar(iter(w), iter([(0, 3), (7, 10)]))
    s = c.spans()
    s.clear()
    assert c.spans() == [(3, 7)]
    assert w == [[0, 10]]


def test_case_08():
    c = Calendar([(-5, -1), (2, 4)], [(-4, -2)])
    assert c.advance(-10, 4) == 4
    assert c.remaining(4) == 0
    with pytest.raises(ValueError): c.advance(-10, 5)
