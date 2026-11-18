import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert records(['@1 INFO: ok']) == [dict(seq=1, level='INFO', message='ok', tags=[])]


def test_case_01():
    assert records(['@2 WARN: x', ' y'])[0]['message'] == 'x\ny'


def test_case_02():
    assert records(['@0 ERROR: ', '+tag red'])[0]['tags'] == ['red']


def test_case_03():
    assert records(['@1 INFO: x', '  y'])[0]['message'] == 'x\n y'


def test_case_04():
    assert records(['@1 INFO: x', '+tag a', '+tag a', '+tag b'])[0]['tags'] == ['a', 'b']


def test_case_05():
    r = records(['@1 INFO: a', '@2 INFO: b', '+tag b'])
    assert r[0]['tags'] == []
    assert r[1]['tags'] == ['b']


def test_case_06():
    for lines in [[' bad'], ['+tag x'], ['@1 INFO: x', '+tag '], ['@1 INFO: x', '@01 WARN: y']]:
        with pytest.raises(ValueError): records(lines)


def test_case_07():
    for line in ['@1 DEBUG: x', '@x INFO: x', '@1 INFO:x', '@١ INFO: x', 'unknown']:
        with pytest.raises(ValueError): records([line])


def test_case_08():
    r = records(iter(['#x', '', '@3 INFO: a', '', '# gap', ' b', '@1 WARN: c']))
    assert [v['seq'] for v in r] == [3, 1]
    assert r[0]['message'] == 'a\nb'
