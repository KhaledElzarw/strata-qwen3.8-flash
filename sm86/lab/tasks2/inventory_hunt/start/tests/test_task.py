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
