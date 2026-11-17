import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert reconcile([{'id': 'a', 'v': 1}], [{'id': 'a', 'v': 2}]) == [('update', 'a', {'v': 2})]


def test_case_01():
    assert reconcile([{'id': 'a'}], [{'id': 'b'}], {'a': 'b'}) == [('rename', 'a', 'b')]


def test_case_02():
    assert reconcile([], [{'id': 'b'}, {'id': 'a'}]) == [('add', {'id': 'a'}), ('add', {'id': 'b'})]
