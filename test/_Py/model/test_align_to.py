import pytest

from caterpillar.py import (
    AlignTo,
    DynamicSizeError,
    StructDefMixin,
    bitfield,
    getstruct,
    pack,
    sizeof,
    struct,
    this,
    union,
    unpack,
)
from caterpillar.shortcuts import f
from caterpillar.types import int3_t, int5_t, uint8_t, uint32_t


# --------------------------------------------------------------------------- #
# AlignTo (spec object) tests
# --------------------------------------------------------------------------- #
def test_align_to_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        AlignTo(0)
    with pytest.raises(ValueError):
        AlignTo(3)


def test_align_to_accepts_dynamic():
    # a callable value is only validated once resolved against a context
    spec = AlignTo(lambda context: 4)
    assert callable(spec.value)


def test_align_to_default_fill_and_strict():
    spec = AlignTo(4)
    assert spec.fill == b"\x00"
    assert spec.strict is True


def test_align_to_fill_bytes():
    spec = AlignTo(8, fill=b"\xde\xad")
    assert spec.fill_bytes(0) == b""
    assert spec.fill_bytes(1) == b"\xde"
    assert spec.fill_bytes(5) == b"\xde\xad\xde\xad\xde"


# --------------------------------------------------------------------------- #
# @struct(align_to=...)
# --------------------------------------------------------------------------- #
def test_struct_align_to_int():
    @struct(align_to=4)
    class Format:
        a: uint8_t

    assert isinstance(getstruct(Format).align_to, AlignTo)
    assert getstruct(Format).align_to.value == 4


def test_struct_align_to_padding():
    @struct(align_to=4)
    class Format:
        a: uint8_t

    assert sizeof(Format) == 4
    obj = Format(a=1)
    assert pack(obj) == b"\x01\x00\x00\x00"
    assert unpack(Format, b"\x01\x00\x00\x00") == obj


def test_struct_align_to_already_aligned():
    @struct(align_to=4)
    class Format:
        a: uint32_t

    assert sizeof(Format) == 4
    obj = Format(a=0x11223344)
    assert pack(obj) == b"\x44\x33\x22\x11"
    assert unpack(Format, b"\x44\x33\x22\x11") == obj


def test_struct_align_to_custom_fill_pattern():
    @struct(align_to=AlignTo(4, fill=b"\xde\xad"))
    class Format:
        a: uint8_t

    obj = Format(a=1)
    assert pack(obj) == b"\x01\xde\xad\xde"
    assert unpack(Format, b"\x01\xde\xad\xde") == obj


def test_struct_align_to_strict_rejects_mismatched_padding():
    @struct(align_to=4)
    class Format:
        a: uint8_t

    with pytest.raises(ValueError):
        unpack(Format, b"\x01\xff\xff\xff")


def test_struct_align_to_lenient_skips_verification():
    @struct(align_to=AlignTo(4, strict=False))
    class Format:
        a: uint8_t

    obj = unpack(Format, b"\x01\xff\xff\xff")
    assert obj.a == 1


def test_struct_align_to_dynamic_value():
    @struct(align_to=this.alignment)
    class Format:
        alignment: uint8_t
        a: uint8_t

    obj = Format(alignment=4, a=1)
    # 2 bytes consumed (alignment + a) -> padded up to the next multiple of 4
    assert pack(obj) == b"\x04\x01\x00\x00"
    assert unpack(Format, b"\x04\x01\x00\x00") == obj


def test_struct_align_to_context_lambda():
    @struct(align_to=lambda context: 4)
    class Format:
        a: uint8_t

    obj = Format(a=1)
    assert pack(obj) == b"\x01\x00\x00\x00"
    assert unpack(Format, b"\x01\x00\x00\x00") == obj


def test_struct_align_to_nested_struct():
    @struct(align_to=4)
    class Inner:
        a: uint8_t

    @struct
    class Outer:
        b: uint8_t
        inner: Inner
        c: uint8_t

    assert sizeof(Inner) == 4
    assert sizeof(Outer) == 6
    obj = Outer(b=1, inner=Inner(a=2), c=3)
    data = b"\x01\x02\x00\x00\x00\x03"
    assert pack(obj) == data
    assert unpack(Outer, data) == obj


def test_struct_align_to_inside_array():
    # Each array element must be individually padded to its own alignment,
    # not just the array as a whole. For array-wide alignment, use Aligned()
    @struct(align_to=4)
    class Small(StructDefMixin):
        a: uint8_t

    @struct
    class Outer:
        items: f[list[Small], Small[2]]

    obj = Outer(items=[Small(a=1), Small(a=2)])
    data = b"\x01\x00\x00\x00\x02\x00\x00\x00"
    assert pack(obj) == data
    unpacked = unpack(Outer, data)
    assert unpacked.items[0] == Small(a=1)
    assert unpacked.items[1] == Small(a=2)


# --------------------------------------------------------------------------- #
# @union(align_to=...)
# --------------------------------------------------------------------------- #
def test_union_align_to_padding():
    @union(align_to=8)
    class U:
        a: uint8_t
        b: uint32_t

    assert sizeof(U) == 8
    obj = U(b=0x11223344, a=0)
    data = pack(obj)
    assert len(data) == 8
    assert data[:4] == b"\x44\x33\x22\x11"
    assert data[4:] == b"\x00\x00\x00\x00"
    unpacked = unpack(U, data)
    assert unpacked.b == 0x11223344


def test_union_align_to_strict():
    @union(align_to=8)
    class U:
        a: uint8_t
        b: uint32_t

    with pytest.raises(ValueError):
        unpack(U, b"\x44\x33\x22\x11\xff\xff\xff\xff")


# --------------------------------------------------------------------------- #
# @bitfield(align_to=...)
# --------------------------------------------------------------------------- #
def test_bitfield_align_to_padding():
    @bitfield(align_to=4)
    class Packet:
        version: int3_t
        type: int5_t

    assert sizeof(Packet) == 4
    obj = Packet(version=1, type=2)
    data = pack(obj)
    assert len(data) == 4
    assert data[1:] == b"\x00\x00\x00"
    assert unpack(Packet, data) == obj


def test_bitfield_align_to_strict():
    @bitfield(align_to=4)
    class Packet:
        version: int3_t
        type: int5_t

    with pytest.raises(ValueError):
        unpack(Packet, b"\x11\xff\xff\xff")


def test_bitfield_align_to_with_bit_group_alignment():
    # alignment= (bit-group alignment, in bits) and align_to= (trailing
    # byte alignment) are independent and must work without interference.
    @bitfield(alignment=16, align_to=8)
    class Both:
        version: int3_t
        type: int5_t

    assert sizeof(Both) == 8
    obj = Both(version=1, type=2)
    data = pack(obj)
    assert len(data) == 8
    assert unpack(Both, data) == obj


def test_bitfield_align_to_dynamic_value():
    @bitfield(align_to=lambda context: 4)
    class Packet:
        version: int3_t
        type: int5_t

    with pytest.raises(DynamicSizeError):
        sizeof(Packet)

    obj = Packet(version=1, type=2)
    data = pack(obj)
    assert len(data) == 4
    assert unpack(Packet, data) == obj
