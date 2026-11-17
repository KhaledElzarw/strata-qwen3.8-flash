import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert layers({'a': [], 'b': ['a']}) == ([['a'], ['b']], [])


def test_case_01():
    assert order({'b': [], 'a': []}) == ['a', 'b']


def test_case_02():
    assert layers({}) == ([], [])


def test_case_03():
    g = {'a': ['b'], 'b': ['a'], 'c': ['b'], 'z': []}
    assert layers(g) == ([['z']], ['a', 'b', 'c'])


def test_case_04():
    assert layers({'a': [], 'b': ['a', 'a']}) == ([['a'], ['b']], [])


def test_case_05():
    with pytest.raises(KeyError): layers({'a': ['x']})
    with pytest.raises(ValueError) as e: order({'a': ['a']})
    assert e.value.args == (('a',),)


def test_case_06():
    g = {'c': ['b'], 'b': ['a'], 'a': []}
    assert layers(g) == ([['a'], ['b'], ['c']], [])


def test_case_07():
    g = {'c': ['a'], 'a': [], 'b': []}
    old = deepcopy(g)
    assert order(g) == ['a', 'b', 'c']
    assert g == old


def test_case_08():
    g = {f'n{i:03}': [] if i == 0 else [f'n{i-1:03}'] for i in range(500)}
    assert len(layers(g)[0]) == 500
