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
