import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert route({'a': [('b', 2)], 'b': []}, 'a', 'b') == (2, ('a', 'b'))


def test_case_01():
    assert route({'a': [], 'b': []}, 'a', 'b') is None


def test_case_02():
    assert route({'a': []}, 'a', 'a') == (0, ('a',))


def test_case_03():
    g = {'s': [('a', 1), ('t', 2)], 'a': [('t', 1)], 't': []}
    assert route(g, 's', 't') == (2, ('s', 't'))


def test_case_04():
    g = {'s': [('b', 1), ('a', 1)], 'a': [('t', 1)], 'b': [('t', 1)], 't': []}
    assert route(g, 's', 't') == (2, ('s', 'a', 't'))


def test_case_05():
    g = {'s': [('s', 0), ('a', 0)], 'a': [('s', 0), ('t', 1)], 't': []}
    assert route(g, 's', 't') == (1, ('s', 'a', 't'))


def test_case_06():
    for g in [{'a': [], 'z': [('x', 1)]}, {'a': [], 'z': [('a', -1)]}, {'a': [('a', True)]}]:
        with pytest.raises((KeyError, ValueError)): route(g, 'a', 'a')
    with pytest.raises(KeyError): route({}, 'a', 'b')


def test_case_07():
    g = {'a': [('b', 9), ('b', 2)], 'b': []}
    old = deepcopy(g)
    assert route(g, 'a', 'b')[0] == 2
    assert g == old


def test_case_08():
    g = {str(i): [(str(i+1), 1)] if i < 299 else [] for i in range(300)}
    r = route(g, '0', '299')
    assert r[0] == 299 and len(r[1]) == 300


def test_case_09():
    assert routes({'a': [('b', 1)], 'b': [], 'c': []}, 'a') == {'a': (0, ('a',)), 'b': (1, ('a', 'b'))}


def test_case_10():
    g = {'s': [('b', 1), ('a', 1)], 'a': [('t', 1)], 'b': [('t', 1)], 't': []}
    assert routes(g, 's')['t'] == (2, ('s', 'a', 't'))


def test_case_11():
    with pytest.raises(KeyError): routes({'a': [], 'z': [('bad', 0)]}, 'a')
    with pytest.raises(KeyError): routes({}, 'a')
