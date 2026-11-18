import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert layers({'a': [], 'b': ['a']}) == ([['a'], ['b']], [])


def test_case_01():
    assert order({'b': [], 'a': []}) == ['a', 'b']


def test_case_02():
    assert layers({}) == ([], [])
