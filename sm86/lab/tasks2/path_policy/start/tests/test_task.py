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
