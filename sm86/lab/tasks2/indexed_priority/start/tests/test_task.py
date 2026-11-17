import pytest
from copy import deepcopy
from task import *

def test_case_00():
    p = Priority()
    p.put('a', 2, 1)
    p.put('b', 1, 2)
    assert p.pop() == ('b', 2)


def test_case_01():
    p = Priority()
    p.put('a', 1, 2)
    assert p.peek() == ('a', 2) and len(p) == 1


def test_case_02():
    p = Priority()
    p.put('a', 1, 2)
    assert p.remove('a')
    assert not p.remove('a')
