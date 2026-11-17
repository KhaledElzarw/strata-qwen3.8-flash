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


def test_case_03():
    s = '{% if a %}A{% if b %}B{% else %}C{% end %}{% else %}D{% end %}'
    assert render(s, {'a': 1, 'b': 0}) == 'AC'


def test_case_04():
    assert render('{% if x %}{{missing}}{% if absent %}bad{% end %}{% end %}', {'x': 0}) == ''


def test_case_05():
    for s in ['{{x', '{{}}', '{% if x %}', '{% else %}', '{% what %}', 'x}}', '%}', '{% if x %}{% else %}{% else %}{% end %}']:
        with pytest.raises(ValueError): render(s, {'x': 0})


def test_case_06():
    with pytest.raises(ValueError): render('{{missing}}{% bad %}', {})
    with pytest.raises(ValueError): render('{% if x %}ok{% else %}{{a.b}}{% end %}', {'x': 1})


def test_case_07():
    with pytest.raises(KeyError): render('{{x}}', {})
    with pytest.raises(KeyError): render('{% if x %}a{% end %}', {})


def test_case_08():
    v = {'x': [], 'n': None}
    assert render('{%  if   x  %}a{%else%}{{n}}{%end%}', v) == 'None'
    assert v == {'x': [], 'n': None}
