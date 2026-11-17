import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert render('hello {{ who }}!', {'who': 'Ada'}) == 'hello Ada!'


def test_case_01():
    assert render('{% if ok %}yes{% else %}no{% end %}', {'ok': 0}) == 'no'


def test_case_02():
    assert render('', {}) == ''
    assert render('a { b', {}) == 'a { b'
