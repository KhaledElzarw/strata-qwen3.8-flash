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


def test_case_03():
    i = Index()
    i.put('a', 'red red')
    i.put('b', 'red')
    i.put('a', 'blue')
    assert i.search('red') == ['b']
    assert i.search('blue') == ['a']


def test_case_04():
    i = Index()
    i.put('a', 'x x y')
    i.put('b', 'x y y')
    assert i.search('x x y') == ['a', 'b']


def test_case_05():
    i = Index()
    i.put('a', 'Straße STRASSE café_foo2bar')
    assert i.terms('a') == {'strasse': 2, 'café': 1, 'foo': 1, 'bar': 1}


def test_case_06():
    i = Index()
    i.put('b', 'x')
    i.put('a', 'x')
    i.put('c', 'x x')
    assert i.search('x') == ['c', 'a', 'b']
    assert i.search('123') == []


def test_case_07():
    i = Index()
    i.put('a', 'x')
    i.put('b', 'x')
    i.remove('a')
    assert i.search('x') == ['b']
    t = i.terms('b')
    t.clear()
    assert i.terms('b') == {'x': 1}


def test_case_08():
    i = Index()
    i.put('a', '')
    assert i.terms('a') == {}
    assert Index().search('x') == []
    with pytest.raises(KeyError): i.terms('missing')
