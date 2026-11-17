import pytest
from copy import deepcopy
from task import *

def test_case_00():
    g = Groups('abc')
    assert g.union('a', 'b')
    assert g.connected('a', 'b')
    assert g.size('a') == 2 and g.count == 2


def test_case_01():
    g = Groups('abc')
    m = g.snapshot()
    g.union('a', 'b')
    g.rollback(m)
    assert not g.connected('a', 'b')


def test_case_02():
    g = Groups('ab')
    assert g.union('a', 'b')
    assert not g.union('b', 'a')
    assert g.snapshot() == 1
