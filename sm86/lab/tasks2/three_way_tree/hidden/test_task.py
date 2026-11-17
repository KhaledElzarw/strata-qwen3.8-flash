import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert merge({'x': 1}, {'x': 2}, {'x': 1}) == ({'x': 2}, [])


def test_case_01():
    assert merge({}, {'a': 1}, {'b': 2}) == ({'a': 1, 'b': 2}, [])


def test_case_02():
    assert merge(0, 1, 2) == (1, [()])


def test_case_03():
    assert merge({'x': 1}, {}, {'x': 2}) == ({}, [('x',)])
    assert merge({'x': 1}, {}, {'x': 1}) == ({}, [])


def test_case_04():
    assert merge({}, {'x': {'a': 1}}, {'x': {'b': 2}}) == ({'x': {'a': 1, 'b': 2}}, [])


def test_case_05():
    assert merge([0, 0], [1, 0], [0, 1]) == ([1, 0], [()])


def test_case_06():
    assert merge({'x': None}, {}, {'x': None}) == ({}, [])
    assert merge({}, {'x': None}, {'x': 1}) == ({'x': None}, [('x',)])


def test_case_07():
    assert merge({'a': [0]}, {'a': [True]}, {'a': [1]}) == ({'a': [True]}, [('a',)])
    assert merge({}, {'z': 1, 'a': 2}, {'z': 2, 'a': 3})[1] == [('a',), ('z',)]


def test_case_08():
    b = {'x': {'y': [1]}}
    l = deepcopy(b)
    r = {'x': {'y': [2]}}
    out, c = merge(b, l, r)
    out['x']['y'].append(3)
    assert b['x']['y'] == [1] and r['x']['y'] == [2]
    assert c == []
