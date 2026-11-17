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
