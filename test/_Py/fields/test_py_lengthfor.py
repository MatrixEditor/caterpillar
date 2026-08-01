import struct as pystruct

import pytest

from caterpillar.py import (
    AsLengthRef,
    BigEndian,
    Bytes,
    String,
    f,
    pack,
    struct,
    this,
    uint8,
    uint16,
    unpack,
)


# --------------------------------------------------------------------------- #
# byte payloads
# --------------------------------------------------------------------------- #
def test_lengthref_pack_updates_length_and_writes_payload():
    @struct(order=BigEndian, kw_only=True)
    class Packet:
        length: f[int, AsLengthRef("length", "payload", uint16)] = 0
        payload: f[bytes, Bytes(this.length)]

    obj = Packet(payload=b"hello")
    assert obj.length == 0
    assert pack(obj) == b"\x00\x05hello"
    assert obj.length == 5


def test_lengthref_unpack_sets_length_for_payload():
    @struct(order=BigEndian, kw_only=True)
    class Packet:
        length: f[int, AsLengthRef("length", "payload", uint16)] = 0
        payload: f[bytes, Bytes(this.length)]

    parsed = unpack(Packet, b"\x00\x05hello")
    assert parsed.length == 5
    assert parsed.payload == b"hello"


def test_lengthref_empty_payload():
    @struct(kw_only=True)
    class Packet:
        length: f[int, AsLengthRef("length", "payload", uint8)] = 0
        payload: f[bytes, Bytes(this.length)]

    obj = Packet(payload=b"")
    assert pack(obj) == b"\x00"
    assert obj.length == 0
    assert unpack(Packet, b"\x00").payload == b""


def test_mod_operator_assigns_length_struct():
    ref = AsLengthRef("length", "payload") % uint8

    @struct(kw_only=True)
    class Packet:
        length: f[int, ref] = 0
        payload: f[bytes, Bytes(this.length)]

    obj = Packet(payload=b"abc")
    assert pack(obj) == b"\x03abc"
    assert obj.length == 3


def test_lengthref_without_struct_raises():
    ref = AsLengthRef("length", "payload")
    with pytest.raises(ValueError):
        _ = pack(None, ref)
    with pytest.raises(ValueError):
        _ = unpack(ref, b"")


def test_lengthref_integer_width_overflow_raises():
    @struct(kw_only=True)
    class Packet:
        length: f[int, AsLengthRef("length", "payload", uint8)] = 0
        payload: f[bytes, Bytes(this.length)]

    with pytest.raises(pystruct.error):
        _ = pack(Packet(payload=b"x" * 256))


def test_repr_names_target_field():
    assert repr(AsLengthRef("length", "payload", uint8)) == "<LengthRef of .payload>"


# --------------------------------------------------------------------------- #
# arrays
# --------------------------------------------------------------------------- #
def test_lengthref_counts_array_elements():
    @struct(order=BigEndian, kw_only=True)
    class Packet:
        count: f[int, AsLengthRef("count", "items", uint8)] = 0
        items: f[list[int], uint16[this.count]]

    obj = Packet(items=[1, 2, 3])
    assert pack(obj) == b"\x03\x00\x01\x00\x02\x00\x03"
    assert obj.count == 3

    parsed = unpack(Packet, b"\x03\x00\x01\x00\x02\x00\x03")
    assert parsed.count == 3
    assert parsed.items == [1, 2, 3]


def test_string_target_length_counts_encoded_bytes():
    @struct(kw_only=True)
    class Packet:
        length: f[int, AsLengthRef("length", "text", uint8)] = 0
        text: f[str, String(this.length)]

    obj = Packet(text="é")
    assert pack(obj) == b"\x02\xc3\xa9"
    assert obj.length == 2
