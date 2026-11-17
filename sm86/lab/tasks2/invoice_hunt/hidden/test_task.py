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


def test_case_03():
    assert invoice([dict(sku='a', quantity=1, price='1.005')])['subtotal'] == '1.01'


def test_case_04():
    r = invoice([dict(sku='a', quantity=2, price='.335')], '.1')
    assert r['subtotal'] == '0.60'


def test_case_05():
    r = invoice([dict(sku='a', quantity=1, price='.005')]*2, tax='.25')
    assert r['subtotal'] == '0.02' and r['tax'] == '0.01'


def test_case_06():
    for v in ['NaN', 'Infinity', '-1', 'bad']:
        with pytest.raises(ValueError): invoice([dict(sku='a', quantity=1, price=v)])
    for q in [0, -1, True]:
        with pytest.raises(ValueError): invoice([dict(sku='a', quantity=q, price='1')])


def test_case_07():
    for d, t in [('1.1', '0'), ('0', '-1'), ('NaN', '0')]:
        with pytest.raises(ValueError): invoice([], d, t)


def test_case_08():
    from decimal import localcontext, ROUND_DOWN
    a = [dict(sku='a', quantity=1, price='123456789012345678901234567.005')]
    with localcontext() as ctx:
        ctx.prec = 6
        ctx.rounding = ROUND_DOWN
        assert invoice(a)['total'] == '123456789012345678901234567.01'
    assert a[0]['price'].endswith('.005')
