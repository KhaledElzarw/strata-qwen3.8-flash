import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert select([('a', 0, 3, 5), ('b', 1, 2, 4), ('c', 3, 4, 2)]) == (7, ('a', 'c'))


def test_case_01():
    assert select([]) == (0, ())


def test_case_02():
    assert select([('b', 0, 2, 5), ('a', 0, 2, 5)]) == (5, ('a',))
