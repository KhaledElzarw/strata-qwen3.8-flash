import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert match({'a': {'x': 2}, 'b': {'y': 3}}) == ((('a', 'x'), ('b', 'y')), 5)


def test_case_01():
    assert match({}) == ((), 0)


def test_case_02():
    assert match({'a': {'x': 3}, 'b': {'x': 1}}) == ((('b', 'x'),), 1)
