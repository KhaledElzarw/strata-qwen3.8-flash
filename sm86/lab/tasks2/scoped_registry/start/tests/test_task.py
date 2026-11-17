import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = Registry()
    r.register('add', lambda a, b=1: a+b)
    assert r.invoke('add', 2, b=3) == 5


def test_case_01():
    r = Registry()
    r.alias('a', 'b')
    r.register('b', lambda: 7)
    assert r.invoke('a') == 7


def test_case_02():
    p = Registry()
    p.register('x', lambda: 1)
    c = Registry(p)
    assert c.invoke('x') == 1
