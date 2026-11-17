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


def test_case_04():
    assert Decoder().feed(b'noise' + bytes([126, 1, 2, 126]) + encode(b'good')) == [b'good']


def test_case_05():
    a, b = encode(b'a'), encode(b'b')
    assert Decoder().feed(a + b[1:]) == [b'a', b'b']


def test_case_06():
    assert Decoder().feed(bytes([126, 1, 125, 126]) + encode(b'x')) == [b'x']


def test_case_07():
    d = Decoder()
    assert d.feed(b'~~~') == []
    assert d.feed(encode(b'x')[:-1]) == []
    assert d.feed(b'~') == [b'x']
    assert Decoder().feed(b'') == []


def test_case_08():
    for payload in [bytes(range(256)), b'~'*3, b'}'*4, bytes([126])]:
        assert Decoder().feed(encode(payload)) == [payload]


def test_case_09():
    d = Decoder()
    d.feed(bytes([126, 1, 2, 126, 125, 126]))
    assert d.errors == 2
    d.feed(b'~~~')
    assert d.errors == 2


def test_case_10():
    d = Decoder()
    d.feed(encode(b'x')[:-1])
    d.finish()
    d.finish()
    assert d.errors == 1
    assert d.feed(encode(b'y')) == [b'y']


def test_case_11():
    d = Decoder()
    d.feed(bytes([126, 125]))
    d.reset()
    assert d.errors == 0
    assert d.feed(encode(b'')) == [b'']
