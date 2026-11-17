import pytest
from copy import deepcopy
from task import *

def test_case_00():
    i = Index()
    i.put('a', 'red blue red')
    assert i.search('red') == ['a']
    assert i.terms('a') == {'red': 2, 'blue': 1}


def test_case_01():
    i = Index()
    i.put('a', 'red')
    i.put('b', 'blue')
    assert i.search('red blue') == []


def test_case_02():
    i = Index()
    i.put('a', 'x')
    assert i.remove('a')
    assert not i.remove('a')
