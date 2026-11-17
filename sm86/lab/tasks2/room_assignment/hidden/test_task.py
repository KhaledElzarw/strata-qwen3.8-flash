import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert assign([('a', 0, 3), ('b', 1, 2)]) == {'a': 0, 'b': 1}


def test_case_01():
    assert conflicts([('z', 0, 3), ('a', 1, 4)]) == [('a', 'z')]


def test_case_02():
    assert assign([]) == {}
    assert conflicts([]) == []


def test_case_03():
    assert assign([('a', 0, 2), ('b', 2, 4)]) == {'a': 0, 'b': 0}


def test_case_04():
    assert assign([('a', 0, 5), ('b', 1, 2), ('c', 5, 6)])['c'] == 0


def test_case_05():
    assert conflicts([('a', 0, 2), ('b', 2, 4), ('c', 1, 1)]) == []


def test_case_06():
    assert assign([('z', 1, 3), ('a', 1, 2), ('x', 1, 2)]) == {'a': 0, 'x': 1, 'z': 2}


def test_case_07():
    for rows in [[('a', 0, 0), ('a', 1, 2)], [('a', 3, 1)]]:
        for fn in [assign, conflicts]:
            with pytest.raises(ValueError): fn(rows)


def test_case_08():
    a = [('e', 2, 2), ('b', -2, 1), ('a', -1, 0)]
    b = a[:]
    assert assign(iter(a)) == {'e': None, 'b': 0, 'a': 1}
    assert conflicts(a) == [('a', 'b')]
    assert a == b


def test_case_09():
    assert utilization(iter([('a', 0, 2), ('b', 2, 5), ('c', 1, 2)])) == {0: 5, 1: 1}


def test_case_10():
    assert utilization([('e', 1, 1)]) == {}
    with pytest.raises(ValueError): utilization([('x', 2, 1)])


def test_case_11():
    assert utilization([('z', 0, 3), ('a', 0, 1), ('b', 3, 4)]) == {1: 3, 0: 2}
