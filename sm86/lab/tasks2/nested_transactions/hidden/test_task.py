import pytest
from copy import deepcopy
from task import *

def test_case_00():
    s = Store({'a': 1})
    s.begin()
    s.set('a', 2)
    s.rollback()
    assert s.get('a') == 1


def test_case_01():
    s = Store()
    s.begin()
    s.set('a', 1)
    s.commit()
    assert s.snapshot() == {'a': 1}


def test_case_02():
    assert Store().depth == 0


def test_case_03():
    s = Store({'a': 1})
    s.begin()
    s.set('a', 2)
    s.begin()
    s.set('a', 3)
    s.commit()
    assert s.depth == 1
    s.rollback()
    assert s.get('a') == 1


def test_case_04():
    s = Store()
    s.begin()
    s.set('a', 1)
    s.begin()
    s.delete('a')
    s.rollback()
    assert s.get('a') == 1
    s.commit()


def test_case_05():
    for method in ['commit', 'rollback']:
        with pytest.raises(ValueError): getattr(Store(), method)()


def test_case_06():
    v = {'a': [1]}
    s = Store(v)
    v['a'].append(2)
    x = s.get('a')
    x.append(3)
    assert s.get('a') == [1]


def test_case_07():
    s = Store()
    v = [1]
    s.set('x', v)
    v.append(2)
    a = s.snapshot()
    a['x'].clear()
    assert s.get('x') == [1]
    assert Store().snapshot() == {}


def test_case_08():
    s = Store()
    with pytest.raises(KeyError): s.get('x')
    with pytest.raises(KeyError): s.delete('x')
    s.begin()
    s.begin()
    s.rollback()
    assert s.depth == 1


def test_case_09():
    s = Store()
    with s.transaction() as same:
        assert same is s
        s.set('x', 1)
    assert s.snapshot() == {'x': 1} and s.depth == 0


def test_case_10():
    s = Store({'x': 0})
    with pytest.raises(RuntimeError):
        with s.transaction():
            s.set('x', 1)
            raise RuntimeError()
    assert s.get('x') == 0 and s.depth == 0


def test_case_11():
    s = Store()
    with pytest.raises(KeyboardInterrupt):
        with s.transaction():
            with s.transaction(): s.set('x', 1)
            raise KeyboardInterrupt()
    assert s.snapshot() == {}
