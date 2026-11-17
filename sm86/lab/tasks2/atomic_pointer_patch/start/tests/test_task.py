import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert apply({'a': 1}, [{'op': 'replace', 'path': '/a', 'value': 2}]) == {'a': 2}


def test_case_01():
    assert apply([1], [{'op': 'add', 'path': '/-', 'value': 2}]) == [1, 2]


def test_case_02():
    assert apply({'a/b': {'~': 3}}, [{'op': 'remove', 'path': '/a~1b/~0'}]) == {'a/b': {}}
