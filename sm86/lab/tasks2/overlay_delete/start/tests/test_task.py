import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert merge({'a': 1}, [{'b': 2}]) == {'a': 1, 'b': 2}


def test_case_01():
    assert merge({'a': {'b': 1}}, [{'a': {'c': 2}}]) == {'a': {'b': 1, 'c': 2}}


def test_case_02():
    assert merge({'a': 1}, [{'a': {'$delete': True}}]) == {}


def test_case_03():
    assert merge({}, [{'x': {'$delete': 1}}]) == {'x': {'$delete': 1}}
