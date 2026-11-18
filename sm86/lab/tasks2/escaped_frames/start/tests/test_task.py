import pytest
from copy import deepcopy
from task import *

def test_case_00():
    assert encode(b'AB') == bytes([126, 65, 66, 131, 126])


def test_case_01():
    assert Decoder().feed(encode(b'hello')) == [b'hello']


def test_case_02():
    assert Decoder().feed(encode(b'')) == [b'']


def test_case_03():
    d = Decoder()
    out = []
    for b in encode(bytes([125, 126])): out.extend(d.feed(bytes([b])))
    assert out == [bytes([125, 126])]
