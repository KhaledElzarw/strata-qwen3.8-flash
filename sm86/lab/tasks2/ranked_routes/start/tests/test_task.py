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
