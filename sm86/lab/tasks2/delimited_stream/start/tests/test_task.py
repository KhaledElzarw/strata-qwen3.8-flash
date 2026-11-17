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
