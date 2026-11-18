import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert load({'a': 'x=1\ny= ${x}/2'}, 'a') == {'x': '1', 'y': '1/2'}


def test_case_01():
    assert load({'a': 'x=old\n@include b\nx=new', 'b': 'y=${x}'}, 'a') == {'x': 'new', 'y': 'new'}


def test_case_02():
    assert load({'a': '# comment\nx =  # literal'}, 'a') == {'x': '# literal'}


def test_case_03():
    assert load({'a': 'x=$${missing} $$ $z'}, 'a') == {'x': '${missing} $ $z'}


def test_case_04():
    for files in [{'a': '@include b', 'b': '@include a'}, {'a': 'x=${y}\ny=${x}'}]:
        with pytest.raises(ValueError): load(files, 'a')


def test_case_05():
    with pytest.raises(KeyError): load({'a': '@include missing'}, 'a')
    with pytest.raises(KeyError): load({'a': 'x=${missing}'}, 'a')


def test_case_06():
    for text in ['bad', '1x=ok', 'x=${}', 'x=${a', '@include b c', 'x=${bad-key}']:
        with pytest.raises(ValueError): load({'a': text}, 'a')


def test_case_07():
    f = {'a': '@include b\nx=changed\n@include b', 'b': 'x=base\ny=${x}'}
    old = deepcopy(f)
    assert load(f, 'a') == {'x': 'base', 'y': 'base'}
    assert f == old


def test_case_08():
    assert load({'a': 'x=${absent}\nx=\ny=${z}\nz=done'}, 'a') == {'x': '', 'y': 'done', 'z': 'done'}
    with pytest.raises(ValueError): load({'a': 'bad\nx=ok'}, 'a')
