import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert bands([(0, 4), (2, 6)]) == [(0, 2, 1), (2, 4, 2), (4, 6, 1)]


def test_case_01():
    assert bands([(0, 2), (2, 4)]) == [(0, 4, 1)]


def test_case_02():
    assert peak([(0, 3), (1, 2)]) == (2, 1)


def test_case_03():
    assert bands([(1, 3)] * 3, 2) == [(1, 3, 3)]


def test_case_04():
    assert bands([(-4, 0), (-2, 2)], 2) == [(-2, 0, 2)]


def test_case_05():
    assert bands(iter([(0, 0), (2, 2)])) == []
    assert peak([]) == (0, None)


def test_case_06():
    with pytest.raises(ValueError): bands([(3, 1)])
    with pytest.raises(ValueError): bands([], 0)


def test_case_07():
    a = [[4, 6], [0, 2]]
    b = deepcopy(a)
    assert peak(iter(a)) == (1, 0)
    assert a == b


def test_case_08():
    assert bands([(0, 2), (0, 4), (2, 4)]) == [(0, 4, 2)]
    assert peak([(0, 2), (3, 5)]) == (1, 0)


def test_case_09():
    assert first_window([(0, 4), (2, 6)], 5) == 0
    assert first_window([(0, 4), (2, 6)], 3, 2) is None


def test_case_10():
    assert first_window(iter([(-3, 0), (0, 3)]), 6) == -3
    with pytest.raises(ValueError): first_window([], 0)


def test_case_11():
    assert first_window([(0, 1), (2, 5)], 2) == 2
    assert first_window([], 1) is None
