import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert parse('1.5 KiB') == 1536


def test_case_01():
    assert parse('1 KB + 24 B') == 1024


def test_case_02():
    assert format_bytes(1536, 'KiB', 2) == '1.50 KiB'


def test_case_03():
    assert parse('-1 KiB + 2 KB - 1.5 B') == parse('974.5 B')


def test_case_04():
    for s in ['', '1', '.5 B', '1. B', '1e3 B', '1 kb', '1 B 2 B', '1 B + -2 B', '1 B +']:
        with pytest.raises(ValueError): parse(s)


def test_case_05():
    from fractions import Fraction
    assert parse('0.1 B') == Fraction(1, 10)
    assert format_bytes(Fraction(-1, 2), 'B', 0) == '-1 B'
    assert format_bytes(Fraction(-1, 1000), 'B', 2) == '0.00 B'


def test_case_06():
    for value, unit, places in [(1.0, 'B', 2), (True, 'B', 2), (1, 'bad', 2), (1, 'B', True), (1, 'B', 7)]:
        with pytest.raises(ValueError): format_bytes(value, unit, places)


def test_case_07():
    assert parse('1GiB-1GB') == 73741824
    assert format_bytes(10**30, 'GB', 0) == '1000000000000000000000 GB'


def test_case_08():
    assert parse(' + 1 B \t + 0.25B ') == parse('1.25 B')
    assert format_bytes(-1500, 'KB', 0) == '-2 KB'
