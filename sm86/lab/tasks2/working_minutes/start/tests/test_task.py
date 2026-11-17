import pytest
from copy import deepcopy
from task import *

def test_case_00():
    c = Calendar([(5, 10), (0, 5)])
    assert c.spans() == [(0, 10)]
    assert c.remaining(3) == 7


def test_case_01():
    assert Calendar([(0, 10)], [(3, 7)]).spans() == [(0, 3), (7, 10)]


def test_case_02():
    assert Calendar([(2, 5), (8, 12)]).advance(0, 5) == 10
