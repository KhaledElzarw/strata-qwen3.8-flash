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


def test_case_03():
    t = [0]
    q = Quota(2, 5, lambda: t[0])
    q.take()
    q.reserve('a', ttl=2)
    t[0] = 2
    assert q.used == 1
    assert not q.commit('a')
    t[0] = 5
    assert q.used == 0


def test_case_04():
    t = [0]
    q = Quota(1, 5, lambda: t[0])
    q.reserve('a')
    t[0] = 4
    assert q.commit('a')
    t[0] = 8
    assert q.used == 1
    t[0] = 9
    assert q.used == 0


def test_case_05():
    q = Quota(2, 5, lambda: 0)
    q.reserve('a')
    with pytest.raises(ValueError): q.reserve('a')
    q.commit('a')
    with pytest.raises(ValueError): q.reserve('a')
    assert not q.cancel('a')
    assert q.used == 1


def test_case_06():
    for cap, win in [(0, 1), (1, 0)]:
        with pytest.raises(ValueError): Quota(cap, win, lambda: 0)
    q = Quota(2, 5, lambda: 0)
    for amount, ttl in [(0, None), (1, 0), (-1, 2)]:
        with pytest.raises(ValueError): q.reserve('a', amount, ttl)
    assert q.used == 0


def test_case_07():
    t = [0]
    q = Quota(1, 2, lambda: t[0])
    assert q.reserve('a', ttl=10)
    t[0] = 3
    assert q.used == 1
    assert not q.reserve('b')
    assert not q.cancel('b')


def test_case_08():
    t = [0]
    q = Quota(1, 2, lambda: t[0])
    q.reserve('a')
    t[0] = 2
    assert q.reserve('a')
    assert q.used == 1
