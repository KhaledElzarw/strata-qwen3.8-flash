import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert schedule({'a': (2, []), 'b': (1, ['a'])}, 2) == [('a', 0, 0, 2), ('b', 0, 2, 3)]


def test_case_01():
    assert schedule({}, 1) == []


def test_case_02():
    assert schedule({'b': (2, []), 'a': (1, [])}, 2) == [('a', 0, 0, 1), ('b', 1, 0, 2)]


def test_case_03():
    j = {'a': (2, []), 'b': (2, []), 'c': (1, ['b']), 'd': (1, ['a'])}
    assert schedule(j, 2)[2:] == [('c', 0, 2, 3), ('d', 1, 2, 3)]


def test_case_04():
    j = {'a': (4, []), 'b': (1, []), 'c': (1, [])}
    assert schedule(j, 2) == [('a', 0, 0, 4), ('b', 1, 0, 1), ('c', 1, 1, 2)]


def test_case_05():
    with pytest.raises(ValueError): schedule({'a': (1, ['b']), 'b': (1, ['a']), 'z': (1, [])}, 2)
    with pytest.raises(KeyError): schedule({'a': (1, ['x'])}, 2)


def test_case_06():
    with pytest.raises(ValueError): schedule({}, 0)
    with pytest.raises(ValueError): schedule({'a': (0, [])}, 1)


def test_case_07():
    j = {'a': (1, []), 'b': (1, ['a', 'a'])}
    old = deepcopy(j)
    assert schedule(j, 1)[1] == ('b', 0, 1, 2)
    assert j == old


def test_case_08():
    j = {f'j{i:03}': (1, [] if i == 0 else [f'j{i-1:03}']) for i in range(200)}
    r = schedule(j, 4)
    assert len(r) == 200 and r[-1] == ('j199', 0, 199, 200)
