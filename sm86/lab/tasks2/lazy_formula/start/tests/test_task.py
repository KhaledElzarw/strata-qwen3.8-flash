import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert evaluate(('add', 2, ('mul', 3, 4)), {}) == 14


def test_case_01():
    assert evaluate(('if', 0, 'missing', 7), {}) == 7


def test_case_02():
    assert evaluate(('let', 'x', 3, ('add', 'x', 1)), {'x': 9}) == 4
