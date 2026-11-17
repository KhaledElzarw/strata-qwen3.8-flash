import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert parse('1.5 KiB') == 1536


def test_case_01():
    assert parse('1 KB + 24 B') == 1024


def test_case_02():
    assert format_bytes(1536, 'KiB', 2) == '1.50 KiB'
