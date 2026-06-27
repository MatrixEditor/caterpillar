import struct as pystruct

import pytest

from caterpillar.py import (
    BigEndian,
    Bytes,
    Prefixed,
    ValidationError,
    pack,
    uint8,
    uint16,
    unpack,
)


def test_prefixed_pack_unpack():
    field = Prefixed(uint8)
    assert pack(b"foo", field) == b"\x03foo"
    assert unpack(field, b"\x03foo") == b"foo"


def test_empty_payload_uses_zero_prefix():
    field = Prefixed(uint8)
    assert pack(b"", field) == b"\x00"
    assert unpack(field, b"\x00") == b""


def test_uint16_prefix_defaults_to_little_endian():
    field = Prefixed(uint16)
    assert pack(b"abc", field) == b"\x03\x00abc"
    assert unpack(field, b"\x03\x00abc") == b"abc"


def test_uint16_prefix_respects_big_endian_order():
    field = Prefixed(uint16)
    assert pack(b"abc", field, order=BigEndian) == b"\x00\x03abc"
    assert unpack(field, b"\x00\x03abc", order=BigEndian) == b"abc"


def test_prefix_integer_width_overflow_raises():
    with pytest.raises(pystruct.error):
        _ = pack(b"x" * 256, Prefixed(uint8))


def test_encoding_prefix_counts_encoded_bytes():
    field: Prefixed[str] = Prefixed(uint8, encoding="utf-8")
    assert pack("hé", field) == b"\x03h\xc3\xa9"
    assert unpack(field, b"\x03h\xc3\xa9") == "hé"


def test_struct_payload_pack_unpack():
    field = Prefixed(uint8, Bytes(...))
    assert pack(b"foo", field) == b"\x03foo"
    assert unpack(field, b"\x03foo") == b"foo"


def test_struct_payload_prefix_counts_serialized_bytes_not_elements():
    field = Prefixed(uint8, uint16[...])
    assert pack([0x0102, 0x0304], field, order=BigEndian) == b"\x04\x01\x02\x03\x04"
    assert unpack(field, b"\x04\x01\x02\x03\x04", order=BigEndian) == [0x0102, 0x0304]


def test_raw_prefixed_truncated_payload_raises():
    with pytest.raises(ValidationError):
        _ = unpack(Prefixed(uint8), b"\x05abc")


def test_inner_struct_must_consume_all_prefixed_bytes():
    with pytest.raises(ValidationError):
        _ = unpack(Prefixed(uint8, Bytes(2)), b"\x03abc")


def test_array_of_prefixed_payloads():
    seq = Prefixed(uint8)[2]
    assert pack([b"a", b"bc"], seq) == b"\x01a\x02bc"
    assert unpack(seq, b"\x01a\x02bc") == [b"a", b"bc"]
