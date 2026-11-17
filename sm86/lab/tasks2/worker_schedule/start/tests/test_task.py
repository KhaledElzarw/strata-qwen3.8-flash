import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert schedule({'a': (2, []), 'b': (1, ['a'])}, 2) == [('a', 0, 0, 2), ('b', 0, 2, 3)]


def test_case_01():
    assert schedule({}, 1) == []


def test_case_02():
    assert schedule({'b': (2, []), 'a': (1, [])}, 2) == [('a', 0, 0, 1), ('b', 1, 0, 2)]
