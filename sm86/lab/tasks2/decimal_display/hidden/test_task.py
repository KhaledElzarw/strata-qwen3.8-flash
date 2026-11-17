import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert format_number('1234.567', grouping=True) == '1,234.57'


def test_case_01():
    assert format_number('2.345') == '2.34'
    assert format_number('2.345', mode='away') == '2.35'


def test_case_02():
    assert parse_display('1,234.50') == parse_display('1234.50')
    assert parse_display('1,234,567.50') == parse_display('1234567.50')


def test_case_03():
    assert format_number('-0.004') == '0.00'
    assert format_number('-2.345', mode='away') == '-2.35'


def test_case_04():
    assert format_number('-2.999', 0, 'zero') == '-2'
    assert format_number('999.999', 2, grouping=True) == '1,000.00'


def test_case_05():
    for text in ['01', '1,23', '0,000', '+1', ' 1', '1e2', '-0.00', '1.2,3', '1.']:
        with pytest.raises(ValueError): parse_display(text)


def test_case_06():
    for text, places, mode in [('NaN', 2, 'even'), ('Infinity', 2, 'even'), ('x', 2, 'even'), ('1', True, 'even'), ('1', 13, 'even'), ('1', 2, 'up')]:
        with pytest.raises(ValueError): format_number(text, places, mode)


def test_case_07():
    from decimal import localcontext
    with localcontext() as ctx:
        ctx.prec = 3
        assert format_number('1234567890.125', 2) == '1234567890.12'


def test_case_08():
    assert format_number('1e-20', 12) == '0.000000000000'
    assert format_number('1e20', 0, grouping=True) == '100,000,000,000,000,000,000'
    assert str(parse_display('-123.450')) == '-123.450'


def test_case_09():
    assert format_column(['1.2', '-1234.5'], grouping=True) == ['     1.20', '-1,234.50']


def test_case_10():
    assert format_column(iter(['2.345', '-0.001']), mode='away') == ['2.35', '0.00']


def test_case_11():
    assert format_column([]) == []
    with pytest.raises(ValueError): format_column([], places=-1)
