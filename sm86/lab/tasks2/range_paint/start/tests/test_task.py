import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = RangeMap()
    r.paint(0, 5, 'a')
    assert r.get(2) == 'a'
    assert r.get(5, 'x') == 'x'


def test_case_01():
    r = RangeMap()
    r.paint(0, 5, 'a')
    r.erase(2, 3)
    assert r.spans() == [(0, 2, 'a'), (3, 5, 'a')]


def test_case_02():
    r = RangeMap()
    r.paint(0, 10, 'a')
    assert r.query(3, 6) == [(3, 6, 'a')]
