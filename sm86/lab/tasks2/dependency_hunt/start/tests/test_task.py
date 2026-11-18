import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert resolve({'a': {1: {}, 2: {}}}, {'a': 1}) == {'a': 1}


def test_case_01():
    assert resolve({'a': {1: {'b': 2}}, 'b': {1: {}, 2: {}}}, {'a': 1}) == {'a': 1, 'b': 2}


def test_case_02():
    assert resolve({'a': {1: {}}}, {}) == {}
