import pytest
from copy import deepcopy
from task import *

def test_case_00():
    w = Warehouse({'a': 5})
    w.reserve('o', {'a': 2})
    assert w.available('a') == 3


def test_case_01():
    w = Warehouse({'a': 5})
    w.reserve('o', {'a': 2})
    w.cancel('o')
    assert w.available('a') == 5 and w.orders() == {}


def test_case_02():
    w = Warehouse({'a': 5})
    w.reserve('o', {'a': 2})
    w.ship('o')
    assert w.available('a') == 3


def test_case_03():
    w = Warehouse({'a': 5, 'b': 1})
    with pytest.raises(ValueError): w.reserve('o', {'a': 2, 'b': 2})
    assert w.available('a') == 5 and w.orders() == {}


def test_case_04():
    w = Warehouse({'a': 5})
    with pytest.raises(KeyError): w.reserve('o', {'a': 1, 'z': 1})
    assert w.available('a') == 5


def test_case_05():
    s = {'a': 5}
    w = Warehouse(s)
    w.reserve('o', {'a': 1})
    assert s == {'a': 5}
    r = w.orders()
    r['o']['a'] = 99
    assert w.orders() == {'o': {'a': 1}}


def test_case_06():
    w = Warehouse({'a': 2})
    w.reserve('o', {'a': 1})
    with pytest.raises(ValueError): w.reserve('o', {'a': 1})
    assert w.available('a') == 1


def test_case_07():
    for q in [-1, 0, True, 1.5]:
        with pytest.raises(ValueError): Warehouse({'a': 3}).reserve('o', {'a': q})
    with pytest.raises(ValueError): Warehouse({'a': -1})
    assert Warehouse({'a': 0}).available('a') == 0


def test_case_08():
    w = Warehouse({'a': 1})
    for f in [lambda: w.cancel('x'), lambda: w.ship('x'), lambda: w.available('x')]:
        with pytest.raises(KeyError): f()
    assert Warehouse({'a': 2}).orders() == {}
