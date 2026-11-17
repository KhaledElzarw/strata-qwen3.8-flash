import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert allocate(5, {'a': 1, 'b': 1}) == {'a': 3, 'b': 2}


def test_case_01():
    assert allocate(10, {'a': 9, 'b': 1}, {'a': 2}) == {'a': 2, 'b': 8}


def test_case_02():
    assert allocate(0, {'a': 1}) == {'a': 0}
    assert allocate(0, {}) == {}


def test_case_03():
    assert allocate(9, {'a': 8, 'b': 1, 'c': 1}, {'a': 2, 'b': 2}) == {'a': 2, 'b': 2, 'c': 5}
