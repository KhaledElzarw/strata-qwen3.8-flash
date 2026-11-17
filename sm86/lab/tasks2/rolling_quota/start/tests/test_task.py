import pytest
from copy import deepcopy
from task import *

def test_case_00():
    q = Quota(2, 5, lambda: 0)
    assert q.take(2)
    assert not q.take()
    assert q.used == 2


def test_case_01():
    q = Quota(2, 5, lambda: 0)
    assert q.reserve('a')
    assert q.commit('a')
    assert not q.commit('a')


def test_case_02():
    q = Quota(2, 5, lambda: 0)
    q.reserve('a')
    assert q.cancel('a')
    assert q.used == 0
