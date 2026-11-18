import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert merge({'a': 1}, [{'b': 2}]) == {'a': 1, 'b': 2}


def test_case_01():
    assert merge({'a': {'b': 1}}, [{'a': {'c': 2}}]) == {'a': {'b': 1, 'c': 2}}


def test_case_02():
    assert merge({'a': 1}, [{'a': {'$delete': True}}]) == {}


def test_case_03():
    assert merge({}, [{'x': {'$delete': 1}}]) == {'x': {'$delete': 1}}


def test_case_04():
    assert merge({'x': 1}, [{'x': {'gone': {'$delete': True}, 'ok': 2}}]) == {'x': {'ok': 2}}


def test_case_05():
    assert merge({'a': [1]}, [{'a': [{'$delete': True}]}]) == {'a': [{'$delete': True}]}
    assert merge({}, [{'x': {'$delete': True, 'more': 1}}]) == {'x': {'$delete': True, 'more': 1}}


def test_case_06():
    a = {'x': [1]}
    b = {'y': [2]}
    r = merge(a, [b])
    r['x'].append(3)
    r['y'].append(4)
    assert a == {'x': [1]} and b == {'y': [2]}


def test_case_07():
    for base, layers in [([], []), ({}, [1])]:
        with pytest.raises(ValueError): merge(base, layers)


def test_case_08():
    assert merge({'a': 0}, iter([{'a': 1}, {'a': {'$delete': True}}, {'a': None}])) == {'a': None}
    assert merge({}, [{'missing': {'$delete': True}}]) == {}


def test_case_09():
    assert explain({'a': {'b': 1}}, [{'a': {'b': 2}}, {'a': {'b': 2}}]) == ({'a': {'b': 2}}, [[('a', 'b')], []])


def test_case_10():
    assert explain({}, [{'x': {'a': 1}}, {'x': {'$delete': True}}]) == ({}, [[('x',)], [('x',)]])


def test_case_11():
    assert explain({'a': [True]}, [{'a': [1]}])[1] == [[('a',)]]
