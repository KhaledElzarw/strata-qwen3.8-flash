import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert allocate(5, {'a': 1, 'b': 1}) == {'a': 3, 'b': 2}


def test_case_01():
    assert allocate(10, {'a': 9, 'b': 1}, {'a': 2}) == {'a': 2, 'b': 8}


def test_case_02():
    assert allocate(0, {'a': 1}) == {'a': 0}
    assert allocate(0, {}) == {}


def test_case_03():
    assert allocate(9, {'a': 8, 'b': 1, 'c': 1}, {'a': 2, 'b': 2}) == {'a': 2, 'b': 2, 'c': 5}


def test_case_04():
    assert allocate(2, {'c': 1, 'b': 1, 'a': 1}) == {'a': 1, 'b': 1, 'c': 0}


def test_case_05():
    assert allocate(2, {'a': 1, 'b': 1}, {'a': 0}) == {'a': 0, 'b': 2}
    with pytest.raises(ValueError): allocate(3, {'a': 1}, {'a': 2})


def test_case_06():
    for total, w, caps in [(True, {'a': 1}, {}), (1, {'a': 0}, {}), (1, {'a': 1}, {'x': 1}), (1, {}, {}), (1, {'a': 1}, {'a': -1})]:
        with pytest.raises(ValueError): allocate(total, w, caps)


def test_case_07():
    n = 10**30
    assert allocate(3, {'b': n, 'a': n+1}) == {'a': 2, 'b': 1}


def test_case_08():
    w, c = {'a': 2, 'b': 1}, {'a': 3}
    old = deepcopy((w, c))
    assert allocate(5, w, c) == {'a': 3, 'b': 2}
    assert (w, c) == old


def test_case_09():
    assert changes(4, {'a': 1, 'b': 1}, {'a': 4}) == [('a', -2), ('b', 2)]


def test_case_10():
    for previous in [{'x': 0}, {'a': -1}, {'a': True}]:
        with pytest.raises(ValueError): changes(1, {'a': 1}, previous)


def test_case_11():
    previous = {'a': 2, 'b': 2}
    assert changes(4, {'a': 1, 'b': 1}, previous) == []
    assert previous == {'a': 2, 'b': 2}
