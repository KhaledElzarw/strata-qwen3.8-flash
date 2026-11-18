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


def test_case_04():
    assert parse(r'X; a="say \"yes\""; b="c\\d"') == ('x', {'a': 'say "yes"', 'b': 'c\\d'})


def test_case_05():
    for s in ['X;a=1;A=2', 'X;a=', 'X;', ';a=1', 'X;1a=b']:
        with pytest.raises(ValueError): parse(s)


def test_case_06():
    for s in ['X;a="x', 'X;a="x"z', 'X;a=two words']:
        with pytest.raises(ValueError): parse(s)


def test_case_07():
    for s in ['X\na=1', 'X;a="x\ry"']:
        with pytest.raises(ValueError): parse(s)


def test_case_08():
    assert parse('X	; Ab_C-2	=	123 	') == ('x', {'ab_c-2': '123'})


def test_case_09():
    assert format_header(' X ', {'B': '2', 'A': ''}) == 'x; a=""; b="2"'


def test_case_10():
    params = {'Q': 'a"b\\c;d'}
    assert parse(format_header('x', params)) == ('x', {'q': params['Q']})


def test_case_11():
    for main, params in [('x;y', {}), ('x', {'A': '1', 'a': '2'}), ('x', {'1x': 'a'}), ('x', {'a': '\n'})]:
        with pytest.raises(ValueError): format_header(main, params)
