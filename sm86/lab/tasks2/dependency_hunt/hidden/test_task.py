import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert resolve({'a': {1: {}, 2: {}}}, {'a': 1}) == {'a': 1}


def test_case_01():
    assert resolve({'a': {1: {'b': 2}}, 'b': {1: {}, 2: {}}}, {'a': 1}) == {'a': 1, 'b': 2}


def test_case_02():
    assert resolve({'a': {1: {}}}, {}) == {}


def test_case_03():
    c = {'a': {1: {'b': 3}, 2: {}}, 'b': {3: {}}}
    assert resolve(c, {'a': 1}) == {'a': 2}


def test_case_04():
    c = {'a': {1: {'b': 2}, 2: {'b': 1}}, 'b': {1: {}, 2: {}}}
    assert resolve(c, {'a': 1}) == {'a': 1, 'b': 2}


def test_case_05():
    c = {'a': {1: {'b': 1}}, 'b': {1: {'a': 1}}}
    assert resolve(c, {'a': 1}) == {'a': 1, 'b': 1}


def test_case_06():
    for c, r in [({}, {'x': 1}), ({'a': {1: {}}}, {'a': 2}), ({'a': {1: {'x': 1}}}, {'a': 1})]:
        with pytest.raises(ValueError): resolve(c, r)


def test_case_07():
    c = {'a': {1: {'b': 1, 'c': 1}}, 'b': {1: {'d': 1}}, 'c': {1: {'d': 2}}, 'd': {1: {}, 2: {}}}
    old = deepcopy(c)
    assert resolve(c, {'a': 1}) == {'a': 1, 'b': 1, 'c': 1, 'd': 2}
    assert c == old


def test_case_08():
    assert resolve({'a': {1: {}}, 'unused': {1: {'missing': 1}}}, {'a': 1}) == {'a': 1}
    assert resolve({'a': {1: {'b': 2}, 2: {}}, 'b': {1: {}}}, {'a': 1}) == {'a': 2}
