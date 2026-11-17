import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert components({'a': ['b'], 'b': ['a'], 'c': []}) == [('a', 'b'), ('c',)]


def test_case_01():
    assert condense({'a': ['b'], 'b': ['a', 'c'], 'c': []}) == ([('a', 'b'), ('c',)], [(0, 1)])


def test_case_02():
    assert reachable({'a': ['b'], 'b': [], 'c': []}, 'a') == ['a', 'b']


def test_case_03():
    assert condense({'z': ['a', 'a', 'z'], 'a': []}) == ([('a',), ('z',)], [(1, 0)])


def test_case_04():
    assert components({}) == []
    assert condense({}) == ([], [])
    assert reachable({'a': ['a']}, 'a') == ['a']


def test_case_05():
    for fn in [components, condense, lambda g: reachable(g, 'a')]:
        with pytest.raises(KeyError): fn({'a': [], 'z': ['missing']})
    with pytest.raises(KeyError): reachable({}, 'x')


def test_case_06():
    g = {'a': ['b'], 'b': ['c'], 'c': ['a', 'd'], 'd': ['e'], 'e': ['d']}
    assert components(g) == [('a', 'b', 'c'), ('d', 'e')]
    assert reachable(g, 'd') == ['d', 'e']


def test_case_07():
    g = {str(i): [str(i+1)] if i < 1199 else [] for i in range(1200)}
    assert len(components(g)) == 1200
    assert len(reachable(g, '0')) == 1200


def test_case_08():
    g = {'a': ['b'], 'b': []}
    old = deepcopy(g)
    assert condense(g)[1] == [(0, 1)]
    assert g == old
    assert components({'a': iter(['b']), 'b': iter(['a'])}) == [('a', 'b')]
