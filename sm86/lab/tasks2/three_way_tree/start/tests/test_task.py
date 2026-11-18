import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert merge({'x': 1}, {'x': 2}, {'x': 1}) == ({'x': 2}, [])


def test_case_01():
    assert merge({}, {'a': 1}, {'b': 2}) == ({'a': 1, 'b': 2}, [])


def test_case_02():
    assert merge(0, 1, 2) == (1, [()])
