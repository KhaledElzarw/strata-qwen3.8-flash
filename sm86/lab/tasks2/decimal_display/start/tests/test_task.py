import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert format_number('1234.567', grouping=True) == '1,234.57'


def test_case_01():
    assert format_number('2.345') == '2.34'
    assert format_number('2.345', mode='away') == '2.35'


def test_case_02():
    assert parse_display('1,234.50') == parse_display('1234.50')
    assert parse_display('1,234,567.50') == parse_display('1234567.50')


def test_case_03():
    assert format_number('-0.004') == '0.00'
    assert format_number('-2.345', mode='away') == '-2.35'
