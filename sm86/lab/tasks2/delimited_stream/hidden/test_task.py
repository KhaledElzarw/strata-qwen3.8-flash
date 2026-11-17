import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = Reader()
    assert r.feed('a,b\nc,d') == [['a', 'b']]
    assert r.finish() == [['c', 'd']]


def test_case_01():
    r = Reader()
    assert r.feed('"a,b",x\n') == [['a,b', 'x']]
    assert r.finish() == []


def test_case_02():
    r = Reader(';')
    assert r.feed('a;;\n') == [['a', '', '']]


def test_case_03():
    r = Reader()
    out = []
    for c in '"a""b\nc",z\r\n': out.extend(r.feed(c))
    out.extend(r.finish())
    assert out == [['a"b\nc', 'z']]


def test_case_04():
    r = Reader()
    assert r.feed('\n\n') == [[''], ['']]
    assert r.finish() == []
    assert Reader().finish() == []


def test_case_05():
    for s in ['a"b', '"a"z', 'a\rb']:
        with pytest.raises(ValueError): Reader().feed(s)


def test_case_06():
    for s in ['"open', 'a\r']:
        r = Reader()
        r.feed(s)
        with pytest.raises(ValueError): r.finish()


def test_case_07():
    r = Reader()
    assert r.feed('""') == []
    assert r.finish() == [['']]
    with pytest.raises(ValueError): r.feed('')
    with pytest.raises(ValueError): r.finish()


def test_case_08():
    for sep in ['', 'xx', '\n', '\r', '"']:
        with pytest.raises(ValueError): Reader(sep)
    r = Reader()
    assert r.feed(' a ,"b\rc"') == []
    assert r.finish() == [[' a ', 'b\rc']]
