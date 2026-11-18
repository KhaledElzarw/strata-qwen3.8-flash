import pytest
from copy import deepcopy
from task import *

def test_case_00():
    q = Queue(lambda: 5)
    q.schedule('a', 3, 1)
    assert q.peek() == ('a', 3)
    assert q.pop_due() == [('a', 1)]


def test_case_01():
    q = Queue(lambda: 0)
    q.schedule('a', 1, 2)
    assert q.cancel('a')
    assert not q.cancel('a')
    assert q.peek() is None


def test_case_02():
    q = Queue(lambda: 10)
    q.schedule('a', 1, 2)
    q.schedule('b', 2, 3)
    assert q.pop_due(1) == [('a', 2)]
    assert len(q) == 1


def test_case_03():
    t = [1]
    q = Queue(lambda: t[0])
    q.schedule('a', 1, 'old')
    q.schedule('a', 5, 'new')
    assert q.pop_due() == []
    t[0] = 5
    assert q.pop_due() == [('a', 'new')]


def test_case_04():
    q = Queue(lambda: 2)
    q.schedule('a', 2, 1)
    assert q.pop_due() == [('a', 1)]


def test_case_05():
    q = Queue(lambda: 3)
    q.schedule('a', 1, 1)
    q.schedule('b', 1, 2)
    q.schedule('a', 1, 3)
    assert q.pop_due() == [('b', 2), ('a', 3)]


def test_case_06():
    q = Queue(lambda: 5)
    q.schedule('a', 1, 1)
    q.cancel('a')
    q.schedule('b', 2, 2)
    assert q.pop_due(0) == []
    assert q.pop_due(1) == [('b', 2)]


def test_case_07():
    q = Queue(lambda: 9)
    q.schedule(None, 1, {})
    q.schedule(1, 1, [])
    assert q.pop_due() == [(None, {}), (1, [])]


def test_case_08():
    q = Queue(lambda: 2)
    q.schedule('a', 1, 1)
    with pytest.raises(ValueError): q.pop_due(-1)
    assert q.peek() == ('a', 1)
    assert q.pop_due() == [('a', 1)]
    assert q.peek() is None
