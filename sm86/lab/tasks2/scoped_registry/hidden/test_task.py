import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = Registry()
    r.register('add', lambda a, b=1: a+b)
    assert r.invoke('add', 2, b=3) == 5


def test_case_01():
    r = Registry()
    r.alias('a', 'b')
    r.register('b', lambda: 7)
    assert r.invoke('a') == 7


def test_case_02():
    p = Registry()
    p.register('x', lambda: 1)
    c = Registry(p)
    assert c.invoke('x') == 1


def test_case_03():
    p = Registry()
    p.register('x', lambda: 1)
    p.alias('a', 'x')
    c = Registry(p)
    c.register('x', lambda: 2)
    assert c.invoke('a') == 2 and p.invoke('a') == 1


def test_case_04():
    r = Registry()
    r.alias('a', 'b')
    r.alias('b', 'a')
    with pytest.raises(ValueError): r.invoke('a')
    with pytest.raises(KeyError): r.invoke('missing')


def test_case_05():
    p = Registry()
    p.register('x', lambda: 1)
    c = Registry(p)
    assert not c.unregister('x')
    c.register('x', lambda: 2)
    assert c.unregister('x')
    assert c.invoke('x') == 1


def test_case_06():
    r = Registry()
    r.alias('z', 'future')
    r.register('a', lambda: 1)
    assert r.names() == ['a', 'z']
    with pytest.raises(ValueError): r.register('a', lambda: 2)
    with pytest.raises(ValueError): r.alias('a', 'b')
    with pytest.raises(ValueError): r.register('', lambda: 2)
    with pytest.raises(ValueError): r.register('b', 2)


def test_case_07():
    register('legacy', lambda x: x*2)
    alias('legacy_alias', 'legacy')
    assert invoke('legacy_alias', 3) == 6
    assert default_registry.invoke('legacy', 2) == 4
    assert names() == ['legacy', 'legacy_alias']
    assert unregister('legacy')
    assert Registry().names() == []


def test_case_08():
    r = Registry()
    def fail(): raise RuntimeError('boom')
    r.register('bad', fail)
    with pytest.raises(RuntimeError): r.invoke('bad')
    p = Registry()
    p.alias('a', 'b')
    c = Registry(p)
    c.alias('b', 'a')
    with pytest.raises(ValueError): c.invoke('a')
