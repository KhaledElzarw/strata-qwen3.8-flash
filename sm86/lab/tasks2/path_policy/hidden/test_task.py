import pytest
from copy import deepcopy
from task import *

def test_case_00():
    p = Policy([('src/*', True)])
    assert p.check('src/a') and not p.check('src/a/b')


def test_case_01():
    p = Policy([('**', True), ('private/**', False)])
    assert not p.check('private/x') and p.check('a/b')


def test_case_02():
    reset()
    add('a', True)
    assert check('a') and default_policy.check('a')
    reset()


def test_case_03():
    p = Policy([('a/**/b', True)])
    assert p.check('a/b') and p.check('a/x/y/b')


def test_case_04():
    a, b = Policy(), Policy()
    a.add('x', True)
    assert not b.check('x')
    b.reset()
    assert a.check('x')


def test_case_05():
    p = Policy([('./a//b/', True)])
    assert p.rules() == [('a/b', True)]
    assert p.check('a/./b')
    r = p.rules()
    r.clear()
    assert p.check('a/b')


def test_case_06():
    p = Policy([('a', True)])
    for s in ['/a', 'a/../b', 'a*']:
        with pytest.raises(ValueError): p.add(s, True)
    with pytest.raises(ValueError): p.add('x', 1)
    assert p.rules() == [('a', True)]


def test_case_07():
    p = Policy([('', True)])
    assert p.check('.') and not p.check('a')
    assert Policy([('*', True)]).check('')
    with pytest.raises(ValueError): p.check('../a')


def test_case_08():
    p = Policy([('**', True), ('**', False), ('A', True)])
    assert p.check('A') and not p.check('a')
    p.reset()
    assert p.rules() == [] and not p.check('A')
