import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert evaluate(('add', 2, ('mul', 3, 4)), {}) == 14


def test_case_01():
    assert evaluate(('if', 0, 'missing', 7), {}) == 7


def test_case_02():
    assert evaluate(('let', 'x', 3, ('add', 'x', 1)), {'x': 9}) == 4


def test_case_03():
    assert evaluate(('and', 0, ('bad',)), {}) == 0
    assert evaluate(('or', 2, None), {}) == 1


def test_case_04():
    assert evaluate(('and', -2, 3), {}) == 1
    assert evaluate(('or', 0, 0), {}) == 0


def test_case_05():
    env = {'x': 4}
    n = ('let', 'x', ('add', 'x', 1), ('let', 'x', ('mul', 'x', 2), 'x'))
    assert evaluate(n, env) == 10
    assert env == {'x': 4}


def test_case_06():
    for n in [True, [], (), ('add', 1), ('bad', 1), ('let', 1, 2, 3), (1, 2)]:
        with pytest.raises(ValueError): evaluate(n, {})


def test_case_07():
    with pytest.raises(KeyError): evaluate(('and', 1, 'missing'), {})
    with pytest.raises(KeyError): evaluate(('let', 'x', 'x', 1), {})


def test_case_08():
    assert evaluate(('if', ('eq', 2, 2), ('lt', 1, 3), ('bad',)), {}) == 1
    assert evaluate(('sub', 9, 4), {}) == 5
