import pytest
from copy import deepcopy
from task import *

def test_case_00():
    c = Catalog()
    c.put('cat', 2)
    c.put('car', 3)
    assert c.suggest('ca') == ['car', 'cat']


def test_case_01():
    c = Catalog()
    c.put('a', 1)
    c.put('ab', 2)
    assert c.longest('abcd') == 'ab'


def test_case_02():
    c = Catalog()
    c.put('x', 0)
    assert c.remove('x')
    assert not c.remove('x')


def test_case_03():
    c = Catalog()
    for w in ['b', 'a', 'c']: c.put(w, 2)
    assert c.suggest('', 2) == ['a', 'b']
    assert c.suggest('', 0) == []
