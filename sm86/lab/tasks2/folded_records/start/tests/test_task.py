import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert records(['@1 INFO: ok']) == [dict(seq=1, level='INFO', message='ok', tags=[])]


def test_case_01():
    assert records(['@2 WARN: x', ' y'])[0]['message'] == 'x\ny'


def test_case_02():
    assert records(['@0 ERROR: ', '+tag red'])[0]['tags'] == ['red']
