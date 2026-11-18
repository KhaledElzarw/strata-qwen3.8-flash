import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = invoice([dict(sku='a', quantity=2, price='3')])
    assert r == {'lines': [('a', '6.00')], 'subtotal': '6.00', 'tax': '0.00', 'total': '6.00'}


def test_case_01():
    assert invoice([], tax='.1')['total'] == '0.00'


def test_case_02():
    assert invoice([dict(sku='a', quantity=1, price='10')], '.2', '.1')['total'] == '8.80'
