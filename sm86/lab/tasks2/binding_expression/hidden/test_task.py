import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert evaluate('2 + 3 * 4') == 14


def test_case_01():
    assert evaluate('-(x + 2)', {'x': 3}) == -5


def test_case_02():
    assert evaluate('20 // 3 % 4') == 2


def test_case_03():
    assert evaluate('10-3-2') == 5
    assert evaluate('--2 * -3') == -6


def test_case_04():
    assert evaluate('-7//3') == -3
    assert evaluate('-7%3') == 2


def test_case_05():
    for s in ['', '1 2', '(1', '1)', '1/', '2**3', '()', 'a.b']:
        with pytest.raises(ValueError): evaluate(s)


def test_case_06():
    with pytest.raises(KeyError): evaluate('absent')
    with pytest.raises(ZeroDivisionError): evaluate('1//0')
    with pytest.raises(ZeroDivisionError): evaluate('1%0')


def test_case_07():
    v = {'_a1': 7}
    assert evaluate(' + _a1 * (2 + 1) ', v) == 21
    assert v == {'_a1': 7}


def test_case_08():
    assert evaluate('1+-2*-3') == 7
    assert evaluate('100//5//2') == 10
    assert evaluate('9%4*3') == 3
