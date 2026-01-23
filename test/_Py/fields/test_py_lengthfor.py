import pytest

from caterpillar.byteorder import BigEndian
from caterpillar.fields.common import Bytes, AsLengthRef, uint8, uint16
from caterpillar.shortcuts import f, this, struct, pack, unpack


@struct(order=BigEndian)
class Format:
    # Syntax is not limited to direct specification-
    # Use the modulo operator to assign a target struct
    # with this length reference:
    # length : uint16 % AsLengthRef("length", "payload") = 0
    # or
    length: f[int, AsLengthRef("length", "payload", uint16)] = 0
    value: f[int, uint8]
    payload: f[bytes, Bytes(this.length)]


def test_lengthref():
    obj = Format(value=1, payload=b"hello")
    # length will be set to 5 when packing the object
    assert len(obj.payload) == 5
    assert obj.length == 0
    assert pack(obj) == b"\x00\x05\x01hello"
    assert obj.length == 5

    data = b"\x00\x05\x01hello"
    assert unpack(Format, data).length == 5
