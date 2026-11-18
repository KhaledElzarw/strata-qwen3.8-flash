import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert Machine().run(['8', '3', '-']) == [5]


def test_case_01():
    m = Machine()
    assert m.run(['4', '=x', '$x', 'dup', '*']) == [16]


def test_case_02():
    assert Machine().run(['1', '2', 'swap', 'drop']) == [2]


def test_case_03():
    assert Machine().run(['-7', '3', '/']) == [-2]


def test_case_04():
    m = Machine()
    m.run(['9', '=x', '5'])
    with pytest.raises(ValueError): m.run(['2', '=x', 'drop', 'drop'])
    assert m.stack == [5] and m.variables == {'x': 9}


def test_case_05():
    for tokens in [['$missing'], ['=bad-name'], ['wat'], ['dup'], ['swap'], ['1', '0', '/']]:
        m = Machine()
        with pytest.raises((ValueError, KeyError, ZeroDivisionError)): m.run(tokens)
        assert m.stack == [] and m.variables == {}


def test_case_06():
    n = 10**100
    assert Machine().run([str(n), '3', '/']) == [n//3]


def test_case_07():
    m = Machine()
    a = m.run(['1'])
    a.append(2)
    assert m.stack == [1]
    assert Machine().stack == []


def test_case_08():
    m = Machine()
    tokens = ['3', '=a', '$a', '2', '+']
    assert m.run(iter(tokens)) == [5]
    assert tokens[-1] == '+'
    assert m.run(['-2', '*']) == [-10]
