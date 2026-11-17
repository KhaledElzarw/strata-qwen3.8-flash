import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert components({'a': ['b'], 'b': ['a'], 'c': []}) == [('a', 'b'), ('c',)]


def test_case_01():
    assert condense({'a': ['b'], 'b': ['a', 'c'], 'c': []}) == ([('a', 'b'), ('c',)], [(0, 1)])


def test_case_02():
    assert reachable({'a': ['b'], 'b': [], 'c': []}, 'a') == ['a', 'b']
