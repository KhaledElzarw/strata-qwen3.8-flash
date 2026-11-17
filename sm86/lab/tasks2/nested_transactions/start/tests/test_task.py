import pytest
from copy import deepcopy
from task import *

def test_case_00():
    s = Store({'a': 1})
    s.begin()
    s.set('a', 2)
    s.rollback()
    assert s.get('a') == 1


def test_case_01():
    s = Store()
    s.begin()
    s.set('a', 1)
    s.commit()
    assert s.snapshot() == {'a': 1}


def test_case_02():
    assert Store().depth == 0


def test_case_03():
    s = Store({'a': 1})
    s.begin()
    s.set('a', 2)
    s.begin()
    s.set('a', 3)
    s.commit()
    assert s.depth == 1
    s.rollback()
    assert s.get('a') == 1
