import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert reconcile([{'id': 'a', 'v': 1}], [{'id': 'a', 'v': 2}]) == [('update', 'a', {'v': 2})]


def test_case_01():
    assert reconcile([{'id': 'a'}], [{'id': 'b'}], {'a': 'b'}) == [('rename', 'a', 'b')]


def test_case_02():
    assert reconcile([], [{'id': 'b'}, {'id': 'a'}]) == [('add', {'id': 'a'}), ('add', {'id': 'b'})]


def test_case_03():
    assert reconcile([{'id': 'a', 'x': 1}], [{'id': 'b', 'y': 2}], {'a': 'b'}) == [('rename', 'a', 'b'), ('update', 'b', {'x': {'$missing': True}, 'y': 2})]


def test_case_04():
    for r in [{'a': 'b', 'b': 'a'}, {'x': 'c'}, {'a': 'missing'}, {'a': 'c', 'b': 'c'}]:
        with pytest.raises(ValueError): reconcile([{'id': 'a'}, {'id': 'b'}], [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}], r)


def test_case_05():
    for rows in [[{'id': 'a'}, {'id': 'a'}], [{}], [{'id': 2}]]:
        with pytest.raises(ValueError): reconcile(rows, [])


def test_case_06():
    assert reconcile([{'id': 'a', 'x': [True]}], [{'id': 'a', 'x': [1]}]) == [('update', 'a', {'x': [1]})]


def test_case_07():
    old = [{'id': 'z'}, {'id': 'a', 'v': 1}]
    new = [{'id': 'b', 'v': [2]}, {'id': 'c'}]
    r = reconcile(old, new, {'a': 'b'})
    assert [x[0] for x in r] == ['remove', 'rename', 'update', 'add']
    r[2][2]['v'].append(3)
    assert new[0]['v'] == [2]


def test_case_08():
    assert reconcile([{'id': 'a'}], [{'id': 'a'}], {'a': 'a'}) == []
    assert reconcile([{'id': 'b'}, {'id': 'a'}], []) == [('remove', 'a'), ('remove', 'b')]
