import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert parse(' Text/Plain ; Charset = utf-8') == ('text/plain', {'charset': 'utf-8'})


def test_case_01():
    assert parse('X; a="b;c"') == ('x', {'a': 'b;c'})


def test_case_02():
    assert parse('A') == ('a', {})


def test_case_03():
    assert parse('X;a="";b=" a "') == ('x', {'a': '', 'b': ' a '})
