import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert round_rows([['.333', '.333', '.334']]) == [['0.33', '0.33', '0.34']]


def test_case_01():
    assert round_rows([['.005', '.005']]) == [['0.01', '0.00']]


def test_case_02():
    assert round_rows([[], ['1']]) == [[], ['1.00']]
