import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert bands([(0, 4), (2, 6)]) == [(0, 2, 1), (2, 4, 2), (4, 6, 1)]


def test_case_01():
    assert bands([(0, 2), (2, 4)]) == [(0, 4, 1)]


def test_case_02():
    assert peak([(0, 3), (1, 2)]) == (2, 1)


def test_case_03():
    assert bands([(1, 3)] * 3, 2) == [(1, 3, 3)]
