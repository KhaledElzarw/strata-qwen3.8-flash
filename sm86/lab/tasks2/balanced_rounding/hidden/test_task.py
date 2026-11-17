import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert round_rows([['.333', '.333', '.334']]) == [['0.33', '0.33', '0.34']]


def test_case_01():
    assert round_rows([['.005', '.005']]) == [['0.01', '0.00']]


def test_case_02():
    assert round_rows([[], ['1']]) == [[], ['1.00']]


def test_case_03():
    assert round_rows([['-.005', '-.005']]) == [['0.00', '-0.01']]


def test_case_04():
    assert round_rows([['2.5'], ['3.5']], 0) == [['2'], ['4']]


def test_case_05():
    assert round_rows([['-1.2', '1.2']], 0) == [['-1', '1']]


def test_case_06():
    for rows, p in [([['NaN']], 2), ([['Infinity']], 2), ([['bad']], 2), ([], True), ([], -1), ([], 7)]:
        with pytest.raises(ValueError): round_rows(rows, p)


def test_case_07():
    from decimal import localcontext
    with localcontext() as c:
        c.prec = 3
        assert round_rows([['1234567890.005', '.005']]) == [['1234567890.01', '0.00']]


def test_case_08():
    a = [['.125', '.125', '.125', '.125']]
    old = deepcopy(a)
    assert round_rows(a) == [['0.13', '0.13', '0.12', '0.12']]
    assert a == old
    assert round_rows([]) == []
