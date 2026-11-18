import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert load({'a': 'x=1\ny= ${x}/2'}, 'a') == {'x': '1', 'y': '1/2'}


def test_case_01():
    assert load({'a': 'x=old\n@include b\nx=new', 'b': 'y=${x}'}, 'a') == {'x': 'new', 'y': 'new'}


def test_case_02():
    assert load({'a': '# comment\nx =  # literal'}, 'a') == {'x': '# literal'}
