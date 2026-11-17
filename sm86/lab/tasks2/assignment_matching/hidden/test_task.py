import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert match({'a': {'x': 2}, 'b': {'y': 3}}) == ((('a', 'x'), ('b', 'y')), 5)


def test_case_01():
    assert match({}) == ((), 0)


def test_case_02():
    assert match({'a': {'x': 3}, 'b': {'x': 1}}) == ((('b', 'x'),), 1)


def test_case_03():
    assert match({'a': {'x': 0, 'y': 100}, 'b': {'x': 0}}) == ((('a', 'y'), ('b', 'x')), 100)


def test_case_04():
    assert match({'b': {'y': 1, 'x': 1}, 'a': {'y': 1, 'x': 1}}) == ((('a', 'x'), ('b', 'y')), 2)


def test_case_05():
    assert match({'a': {'x': -5}, 'b': {'x': -5}, 'c': {}}) == ((('a', 'x'),), -5)


def test_case_06():
    for value in [True, 1.0, '1']:
        with pytest.raises(ValueError): match({'a': {'x': value}})


def test_case_07():
    c = {'a': {'x': 2, 'y': 1}, 'b': {'x': 1, 'y': 2}}
    old = deepcopy(c)
    assert match(c) == ((('a', 'y'), ('b', 'x')), 2)
    assert c == old


def test_case_08():
    c = {f'w{i:02}': {f'j{j:02}': abs(i-j) for j in range(12)} for i in range(20)}
    pairs, cost = match(c)
    assert len(pairs) == 12 and cost == 0
    assert pairs == tuple((f'w{i:02}', f'j{i:02}') for i in range(12))
