import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert assign([('a', 0, 3), ('b', 1, 2)]) == {'a': 0, 'b': 1}


def test_case_01():
    assert conflicts([('z', 0, 3), ('a', 1, 4)]) == [('a', 'z')]


def test_case_02():
    assert assign([]) == {}
    assert conflicts([]) == []


def test_case_03():
    assert assign([('a', 0, 2), ('b', 2, 4)]) == {'a': 0, 'b': 0}
