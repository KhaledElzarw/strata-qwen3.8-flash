import pytest
from copy import deepcopy
from task import *

def test_case_00():
    r = Receiver()
    assert r.receive(0, b'a') == (1, [b'a'])


def test_case_01():
    r = Receiver()
    assert r.receive(1, b'b') == (0, [])
    assert r.receive(0, b'a') == (2, [b'a', b'b'])


def test_case_02():
    r = Receiver()
    r.finish(0)
    assert r.complete


def test_case_03():
    r = Receiver(window=2)
    assert r.receive(2, b'far') == (0, [])
    assert r.receive(0, b'a') == (1, [b'a'])
    assert r.receive(1, b'b') == (2, [b'b'])


def test_case_04():
    r = Receiver()
    r.receive(1, b'first')
    r.receive(1, b'second')
    assert r.receive(0, b'a') == (2, [b'a', b'first'])
    assert r.receive(0, b'x') == (2, [])


def test_case_05():
    r = Receiver()
    r.receive(3, b'c')
    r.finish(2)
    r.receive(1, b'b')
    assert r.receive(0, b'a') == (2, [b'a', b'b'])
    assert r.complete
    assert r.receive(2, b'x') == (2, [])


def test_case_06():
    r = Receiver(start=3)
    assert not r.complete
    r.finish(4)
    r.finish(4)
    with pytest.raises(ValueError): r.finish(5)
    assert r.receive(3, b'') == (4, [b''])
    assert r.complete


def test_case_07():
    for kw in [{'start': -1}, {'window': 0}]:
        with pytest.raises(ValueError): Receiver(**kw)
    r = Receiver()
    with pytest.raises(ValueError): r.receive(-1, b'x')
    r.receive(0, b'a')
    with pytest.raises(ValueError): r.finish(0)


def test_case_08():
    r = Receiver(window=5)
    for s in [4, 2, 3, 1]: r.receive(s, bytes([s]))
    assert r.receive(0, b'z') == (5, [b'z', b'\x01', b'\x02', b'\x03', b'\x04'])
    assert Receiver().ack == 0
