import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert Machine().run(['8', '3', '-']) == [5]


def test_case_01():
    m = Machine()
    assert m.run(['4', '=x', '$x', 'dup', '*']) == [16]


def test_case_02():
    assert Machine().run(['1', '2', 'swap', 'drop']) == [2]
