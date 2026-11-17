import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert evaluate('2 + 3 * 4') == 14


def test_case_01():
    assert evaluate('-(x + 2)', {'x': 3}) == -5


def test_case_02():
    assert evaluate('20 // 3 % 4') == 2
