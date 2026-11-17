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


def test_case_04():
    c = Catalog()
    c.put('a', 2)
    c.put('a', 5)
    assert len(c) == 1 and c.prefix_weight('a') == 5


def test_case_05():
    c = Catalog()
    c.put('a', 0)
    assert c.suggest() == ['a']
    assert c.longest('ax') == 'a'
    assert c.prefix_weight('z') == 0


def test_case_06():
    for w, v in [('', 1), ('a', -1), ('a', True), (3, 2)]:
        with pytest.raises(ValueError): Catalog().put(w, v)
    with pytest.raises(ValueError): Catalog().suggest(limit=-1)


def test_case_07():
    c = Catalog()
    c.put('é', 1)
    c.put('E', 2)
    assert c.suggest() == ['E', 'é']
    assert c.longest('É') is None


def test_case_08():
    c = Catalog()
    c.put('abc', 2)
    c.put('abd', 4)
    c.put('x', 9)
    a = c.suggest('ab')
    a.clear()
    assert c.prefix_weight('ab') == 6
    assert c.suggest('ab') == ['abd', 'abc']
    assert len(Catalog()) == 0


def test_case_09():
    c = Catalog()
    for w, n in [('cat', 2), ('cart', 3), ('cut', 1), ('act', 5)]: c.put(w, n)
    assert c.match('c?t') == ['cat', 'cut']
    assert c.match('c*t') == ['cart', 'cat', 'cut']


def test_case_10():
    c = Catalog()
    c.put('a*b', 2)
    c.put('axb', 3)
    assert c.match(r'a\*b') == ['a*b']
    with pytest.raises(ValueError): c.match(chr(92))


def test_case_11():
    c = Catalog()
    c.put('é', 0)
    assert c.match('?') == ['é']
    assert c.match('**', 0) == []
    with pytest.raises(ValueError): c.match('*', -1)
