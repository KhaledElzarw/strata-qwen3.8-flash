import pytest
from copy import deepcopy
from task import *

def test_case_00():
    c = Coordinator(lambda: 0)
    t = c.acquire('x', 'a', 5)
    assert t == 1
    assert c.acquire('x', 'b', 5) is None
    assert c.write('x', t, 7) and c.read('x') == 7


def test_case_01():
    now = [0]
    c = Coordinator(lambda: now[0])
    t = c.acquire('x', 'a', 5)
    now[0] = 5
    assert not c.write('x', t, 1)
    assert c.acquire('x', 'a', 2) == 2


def test_case_02():
    c = Coordinator(lambda: 0)
    t = c.acquire('x', 'a', 2)
    assert c.release('x', 'a', t)
    assert not c.release('x', 'a', t)
