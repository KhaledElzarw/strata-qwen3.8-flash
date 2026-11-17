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
