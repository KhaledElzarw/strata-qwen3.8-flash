import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert apply({'a': 1}, [{'op': 'replace', 'path': '/a', 'value': 2}]) == {'a': 2}


def test_case_01():
    assert apply([1], [{'op': 'add', 'path': '/-', 'value': 2}]) == [1, 2]


def test_case_02():
    assert apply({'a/b': {'~': 3}}, [{'op': 'remove', 'path': '/a~1b/~0'}]) == {'a/b': {}}


def test_case_03():
    assert apply([1, 3], [{'op': 'add', 'path': '/1', 'value': 2}, {'op': 'remove', 'path': '/0'}]) == [2, 3]


def test_case_04():
    assert apply(3, [{'op': 'add', 'path': '', 'value': {}}, {'op': 'add', 'path': '/', 'value': 2}]) == {'': 2}
    assert apply(3, [{'op': 'remove', 'path': ''}]) is None


def test_case_05():
    for path in ['/01', '/-1', '/~2', 'bad']:
        with pytest.raises(ValueError): apply([], [{'op': 'remove', 'path': path}])


def test_case_06():
    for doc, path in [({}, '/x'), ([], '/0'), ({'a': 1}, '/a/x')]:
        with pytest.raises(KeyError): apply(doc, [{'op': 'replace', 'path': path, 'value': 2}])


def test_case_07():
    a = {'x': [1]}
    ops = [{'op': 'replace', 'path': '/x/0', 'value': 2}, {'op': 'remove', 'path': '/missing'}]
    with pytest.raises(KeyError): apply(a, ops)
    assert a == {'x': [1]}
    assert ops[0]['value'] == 2


def test_case_08():
    with pytest.raises(ValueError): apply({'x': [True]}, [{'op': 'test', 'path': '', 'value': {'x': [1]}}])
    assert apply([1], [{'op': 'test', 'path': '/0', 'value': 1}]) == [1]
    with pytest.raises(ValueError): apply({}, [{'op': 'wat', 'path': ''}])
