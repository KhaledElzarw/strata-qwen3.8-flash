import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert select([('a', 0, 3, 5), ('b', 1, 2, 4), ('c', 3, 4, 2)]) == (7, ('a', 'c'))


def test_case_01():
    assert select([]) == (0, ())


def test_case_02():
    assert select([('b', 0, 2, 5), ('a', 0, 2, 5)]) == (5, ('a',))


def test_case_03():
    assert select([('a', 0, 1, 2), ('b', 1, 2, 3), ('z', 0, 2, 5)]) == (5, ('z',))


def test_case_04():
    assert select([('z', 0, 1, 2), ('a', 2, 3, 2), ('c', 0, 3, 3)], gap=1) == (4, ('z', 'a'))


def test_case_05():
    assert select([('a', 0, 1, 0), ('b', 1, 2, -2)]) == (0, ())


def test_case_06():
    for jobs, gap in [([('a', 0, 0, 1)], 0), ([('a', 0, 1, 1)] * 2, 0), ([], -1)]:
        with pytest.raises(ValueError): select(jobs, gap)


def test_case_07():
    jobs = [('z', 2, 4, 3), ('b', 0, 2, 3), ('a', 0, 1, 3)]
    old = deepcopy(jobs)
    assert select(iter(jobs)) == (6, ('a', 'z'))
    assert jobs == old


def test_case_08():
    jobs = [(str(i).zfill(3), i * 2, i * 2 + 1, 1) for i in range(300)]
    assert select(jobs) == (300, tuple(j[0] for j in jobs))
