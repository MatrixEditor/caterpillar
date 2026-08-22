import pytest

from caterpillar.fields.unnamed import Unnamed, sized
from caterpillar.py import (
    StructDefMixin,
    ValidationError,
    f,
    pack,
    struct,
    this,
    unpack,
)
from caterpillar.types import uint8_t, uint16_t, uint32_t


@struct
class Packet:
    tag: uint8_t
    payload: Unnamed[uint8_t, uint16_t, uint32_t]


@struct
class LengthPrefixed:
    n: uint8_t
    payload: Unnamed[uint8_t, uint16_t].sized(this.n)


@struct
class SizedMarkerPacket:
    tag: uint8_t
    payload: Unnamed[uint8_t, uint16_t, sized[4]]


@struct
class SizedMarkerContextLambda:
    n: uint8_t
    payload: Unnamed[uint8_t, uint16_t, sized[this.n]]


@struct
class Header:
    a: uint8_t
    b: uint8_t


@struct
class Nested:
    payload: Unnamed[Header, uint16_t]


@struct
class Elem(StructDefMixin):
    tag: uint8_t
    payload: Unnamed[uint8_t, uint16_t]


@struct
class Container:
    items: f[list[Elem], Elem[4]]


def test_lazy_decode_via_getitem_and_attr():
    p = unpack(Packet, bytes([0xAB, 0x11, 0x22, 0x33, 0x44]))

    assert repr(p.payload) == "Unnamed(?, ?, ?)"
    assert p.payload[0] == 0x11
    assert p.payload._1 == 0x2211
    assert p.payload[2] == 0x44332211
    assert len(p.payload) == 3


def test_decoded_members_are_cached():
    p = unpack(Packet, bytes([0xAB, 0x11, 0x22, 0x33, 0x44]))
    first = p.payload[0]
    second = p.payload[0]
    assert first == second == 0x11


def test_negative_index_and_iteration():
    p = unpack(Packet, bytes([0xAB, 0x11, 0x22, 0x33, 0x44]))
    assert p.payload[-1] == p.payload[2]
    assert list(p.payload) == [p.payload[0], p.payload[1], p.payload[2]]


def test_slice_returns_plain_tuple():
    p = unpack(Packet, bytes([0xAB, 0x11, 0x22, 0x33, 0x44]))
    assert p.payload[0:2] == (p.payload[0], p.payload[1])


def test_out_of_range_index_raises():
    p = unpack(Packet, bytes([0xAB, 0x11, 0x22, 0x33, 0x44]))
    with pytest.raises(IndexError):
        p.payload[3]


def test_context_lambda_sizing():
    data = bytes([2, 0x01, 0x02])
    p = unpack(LengthPrefixed, data)
    assert p.payload[0] == 1
    assert p.payload[1] == 0x0201
    assert pack(p) == data


def test_sized_marker_overrides_default_size():
    # sized[4] overrides the default (max-of-members == 2) size to 4 bytes,
    # and the marker itself is excluded from the real member count.
    data = bytes([0xAB, 0x11, 0x22, 0x33, 0x44])
    p = unpack(SizedMarkerPacket, data)
    assert len(p.payload) == 2
    assert p.payload[0] == 0x11
    assert p.payload[1] == 0x2211
    assert pack(p) == data


def test_sized_marker_with_context_lambda():
    data = bytes([3, 0x01, 0x02, 0x03])
    p = unpack(SizedMarkerContextLambda, data)
    assert p.payload[0] == 1
    assert p.payload[1] == 0x0201
    assert pack(p) == data


def test_sized_marker_alone_raises():
    with pytest.raises(TypeError):
        Unnamed[sized[10]]


def test_sized_marker_duplicate_raises():
    with pytest.raises(TypeError):
        Unnamed[uint8_t, sized[4], sized[8]]


def test_sized_marker_not_last_raises():
    with pytest.raises(TypeError):
        Unnamed[sized[4], uint8_t, uint16_t]


def test_nested_struct_member():
    data = bytes([0x10, 0x20])
    p = unpack(Nested, data)
    assert p.payload[0] == Header(a=0x10, b=0x20)
    assert isinstance(p.payload[0], Header)
    assert p.payload[1] == 0x2010
    assert pack(p) == data


def test_array_of_unions_independence():
    data = bytes(
        [
            0x01,
            0xAA,
            0xBB,
            0x02,
            0xCC,
            0xDD,
            0x03,
            0xEE,
            0xFF,
            0x04,
            0x11,
            0x22,
        ]
    )
    c = unpack(Container, data)

    assert c.items[3].payload[0] == 0x11
    assert c.items[0].payload[0] == 0xAA
    assert c.items[2].payload[1] == 0xFFEE
    assert c.items[1].payload[0] == 0xCC
    assert pack(c) == data


def test_empty_constr():
    u = Unnamed()
    assert len(u) == 0
    assert list(u) == []
    assert repr(u) == "Unnamed()"


def test_positional_constr():
    u = Unnamed(1, 2, 3)
    assert len(u) == 3
    assert u[0] == 1
    assert u[1] == 2
    assert u._2 == 3
    assert tuple(u) == (1, 2, 3)


def test_keyword_constr():
    u = Unnamed(_3=0xBEEF)
    assert len(u) == 4
    assert u[3] == 0xBEEF
    with pytest.raises(AttributeError):
        u[0]


def test_duplicate_index_assignment():
    with pytest.raises(TypeError):
        Unnamed(1, 2, _0=99)


def test_unknown_keyword_raises():
    with pytest.raises(TypeError):
        Unnamed(x=1)


def test_last_assigned_value_is_packed():
    u = Unnamed(1, 2, 3)
    out = pack(Packet(tag=9, payload=u))
    reparsed = unpack(Packet, out)
    assert reparsed.payload[2] == 3
    assert len(out) == 5


def test_pack_with_nothing_set_raises():
    with pytest.raises(ValidationError):
        pack(Packet(tag=1, payload=Unnamed()))
