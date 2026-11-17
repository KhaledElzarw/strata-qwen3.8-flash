import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert encode([['a', 'b'], ['c', 'd']]) == 'a\tb\nc\td'
    assert decode('a\tb') == [['a', 'b']]


def test_case_01():
    c = Codec(('int', 'bool'))
    assert c.encode([[3, False]]) == '3\tfalse'
    assert c.decode('-2\ttrue') == [[-2, True]]


def test_case_02():
    c = Codec(('nullable', 'nullable'))
    assert c.decode(c.encode([[None, r'\N']])) == [[None, r'\N']]


def test_case_03():
    rows = [['a\tb', 'c\nd', 'e\rf', 'g\\h']]
    assert decode(encode(rows)) == rows


def test_case_04():
    for s in ['00', '-0', '+1', ' 1', '1.0']:
        with pytest.raises(ValueError): Codec(('int',)).decode(s)


def test_case_05():
    for s in ['True', '1', 'FALSE']:
        with pytest.raises(ValueError): Codec(('bool',)).decode(s)
    with pytest.raises(ValueError): Codec(('int',)).encode([[True]])


def test_case_06():
    for s in [r'a\q', 'a' + chr(92)]:
        with pytest.raises(ValueError): decode(s)
    with pytest.raises(ValueError): Codec(('int', 'str')).decode('1')


def test_case_07():
    assert decode('') == []
    assert Codec(('int',)).encode([]) == ''
    with pytest.raises(ValueError): Codec(('bad',))
    with pytest.raises(ValueError): Codec(('str',)).encode([[1]])


def test_case_08():
    rows = [[1, 'x']]
    a = Codec(('int', 'str'))
    b = Codec(('str',))
    assert a.decode(a.encode(rows)) == rows
    assert rows == [[1, 'x']]
    assert b.decode('2') == [['2']]
