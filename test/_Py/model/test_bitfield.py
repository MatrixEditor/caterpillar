import enum

import pytest

from caterpillar.model import (
    Bitfield,
    bitfield,
    EndGroup,
    SetAlignment,
    sizeof,
    unpack,
    CharFactory,
    pack,
    Invisible
)
from caterpillar.options import (
    S_REPLACE_TYPES,
)
from caterpillar.fields import uint16, Bytes, uint8
from caterpillar.py import BigEndian, LittleEndian, ValidationError, int8
from caterpillar.shared import getstruct
from caterpillar.shortcuts import f
from caterpillar.types import (
    balign_t,
    int1_t,
    int2_t,
    int3_t,
    uint16_t,
    uint24_t,
    uint32_t,
)


def test_bitfield_syntax__standard():
    # Syntax no. 1
    @bitfield
    class FormatA:
        a: f[int, 3 - uint16]

    bfield = getstruct(FormatA)
    assert isinstance(bfield, Bitfield)
    groups = bfield.groups
    assert len(groups) == 1
    assert not groups[0].is_empty()
    # default alignment is 0x08 unless B_OVERWRITE_ALIGNMENT is set
    assert groups[0].bit_count == 0x08
    assert groups[0].entries[0].width == 3


def test_bitfield_syntax__align():
    # Syntax no. 1 + no. 2
    @bitfield
    class FormatA:
        a: f[int, 3]
        # either specify manually (typing compliant)
        # _: f[None, 0] = None
        # or use the pre-defined type
        _: balign_t = Invisible()
        # or use syntax direclty (pyright will scream at you)
        # _: 0
        b: f[int, 4]

    bfield = getstruct(FormatA)
    assert isinstance(bfield, Bitfield)
    groups = bfield.groups
    assert len(groups) == 2

    # The alignment syntax finalizes the first group and start a new one
    a = groups[0]
    b = groups[1]
    assert a.bit_count == 0x08 and b.bit_count == 0x08
    assert a.entries[0].width == 3
    assert b.entries[0].width == 4


def test_bitfield_syntax__struct():
    # syntax no. 3 (generic struct)
    @bitfield
    class FormatA:
        a: uint16_t
        b: uint32_t
        c: uint24_t

    # just like a @struct definition
    assert sizeof(FormatA) == 2 + 4 + 3


def test_bitfield_syntax__field_factory():
    # syntax no. 4
    @bitfield
    class FormatA:
        a: f[int, (uint16, int)]  # this won't work
        b: f[str, (5 - uint8, str)]

    struct = getstruct(FormatA)
    assert struct is not None
    assert isinstance(struct, Bitfield)

    groups = struct.groups
    assert len(groups) == 2
    # The first definition will revert to a simple field, because
    # no bits are given
    assert groups[0].is_field() is True
    # conversion to string
    assert groups[1].entries[0].factory.target is str


def test_bitfield_syntax__extended():
    class SimpleEnum(enum.IntEnum):
        A = 0
        B = 1
        C = 2

    # syntax no. 5
    @bitfield
    class FormatA:
        # Explanation:
        # 4bits converted to string
        a1: f[str, (4, str)]
        # 2bits converted to Enum
        a2: f[SimpleEnum | int, (2, SimpleEnum)]
        # alignment is 8 bits, finalize group and set alignment
        # to 16bits for next group
        _: f[None, (0, SetAlignment(16))] = Invisible()
        # 10bits entry for current group, then finalize group
        b1: f[int, (10, EndGroup)]
        # 12bits in new group
        c1: f[int, 12]

    # We should see exactly three groups here
    bfield = getstruct(FormatA)
    assert isinstance(bfield, Bitfield)
    groups = bfield.groups
    assert len(groups) == 3
    assert groups[0].bit_count == 8
    assert groups[1].bit_count == 16
    assert groups[2].bit_count == 16

    assert len(groups[0].entries) == 2
    assert groups[0].entries[1].factory.target is SimpleEnum


def test_bitfield__replace_types():
    class SimpleEnum(enum.IntEnum):
        A = 0
        B = 1
        C = 2

    @bitfield(options={S_REPLACE_TYPES})
    class FormatA:
        a1: f[str, (4, str)]  # a1: str
        a2: f[SimpleEnum, (2, SimpleEnum)]  # a2: SimpleEnum
        _: balign_t = Invisible()
        b1: f[bytes, Bytes(6)]  # b1: bytes

    annotations = FormatA.__annotations__
    assert annotations["a1"] is str
    assert annotations["a2"] is SimpleEnum
    assert annotations["b1"] is bytes


def test_bitfield__unpack():
    # same as before
    class SimpleEnum(enum.IntEnum):
        A = 0
        B = 1
        C = 2

    @bitfield
    class FormatA:
        a1: f[str, (4, CharFactory)]  # a1: str
        a2: f[SimpleEnum, (2, SimpleEnum)]  # a2: SimpleEnum
        _: balign_t = Invisible()
        b1: f[bytes, Bytes(6)]  # b1: bytes

    # 0b00110100.to_bytes()
    data = b"4" + b"12" * 3
    obj = unpack(FormatA, data)
    assert obj.a1 == "\x03"
    assert obj.a2 == SimpleEnum.B
    assert obj.b1 == b"12" * 3


def test_bitfield__pack():
    @bitfield
    class FormatA:
        a1: int1_t
        a2: int2_t
        a3: int3_t
        _: balign_t = Invisible()
        b1: uint16_t

    obj = FormatA(a1=True, a2=3, a3=5, b1=0xFF00)
    # 0b1_11_101_00.to_bytes()
    assert pack(obj) == b"\xf4" + b"\x00\xff"


# --------------------------------------------------------------------------- #
# cross-byte packing and byte order
# --------------------------------------------------------------------------- #
def test_big_endian_bitfield_packs_msb_first():
    @bitfield(order=BigEndian)
    class Cross:
        a: f[int, 5]
        b: f[int, 7]

    obj = Cross(0b10101, 0b1100110)

    assert sizeof(Cross) == 2
    assert pack(obj) == bytes.fromhex("ae60")
    assert unpack(Cross, bytes.fromhex("ae60")) == obj


def test_little_endian_bitfield_reverses_storage_bytes_not_field_order():
    @bitfield(order=LittleEndian)
    class Cross:
        a: f[int, 5]
        b: f[int, 7]

    obj = Cross(0b10101, 0b1100110)

    assert sizeof(Cross) == 2
    assert pack(obj) == bytes.fromhex("60ae")
    assert unpack(Cross, bytes.fromhex("60ae")) == obj


# --------------------------------------------------------------------------- #
# alignment and trailing bits
# --------------------------------------------------------------------------- #
def test_trailing_bits_are_zero_padded():
    @bitfield(order=BigEndian)
    class Partial:
        value: f[int, 3]

    assert sizeof(Partial) == 1
    assert pack(Partial(0b101)) == b"\xa0"
    assert unpack(Partial, b"\xa0") == Partial(0b101)


def test_alignment_for_sixteen_bit_group():
    @bitfield(order=BigEndian)
    class Aligned:
        a: f[int, 3]
        _: f[None, (0, SetAlignment(16))] = Invisible()
        b: f[int, 10]

    obj = Aligned(a=0b101, b=0x2AA)

    assert [group.bit_count for group in getstruct(Aligned).groups] == [8, 16]
    assert sizeof(Aligned) == 3
    assert pack(obj) == bytes.fromhex("a0aa80")
    assert unpack(Aligned, bytes.fromhex("a0aa80")) == obj


def test_end_group_starts_new_aligned_byte_group():
    @bitfield(order=BigEndian)
    class Groups:
        a: f[int, (4, EndGroup)]
        b: f[int, 4]

    obj = Groups(0xA, 0xB)

    assert [group.bit_count for group in getstruct(Groups).groups] == [8, 8]
    assert pack(obj) == bytes.fromhex("a0b0")
    assert unpack(Groups, bytes.fromhex("a0b0")) == obj


# --------------------------------------------------------------------------- #
# factories
# --------------------------------------------------------------------------- #
def test_bitfield_enum_and_char_factories():
    class Mode(enum.IntEnum):
        ZERO = 0
        ONE = 1
        TWO = 2

    @bitfield(order=BigEndian)
    class Factories:
        ch: f[str, (8, CharFactory)]
        mode: f[Mode, (2, Mode)]

    obj = Factories("A", Mode.TWO)
    parsed = unpack(Factories, bytes.fromhex("4180"))

    assert pack(obj) == bytes.fromhex("4180")
    assert parsed == obj
    assert parsed.mode is Mode.TWO
    assert parsed.ch == "A"


def test_signed_bitfield_unpack_sign_extends_from_declared_width():
    @bitfield(order=BigEndian)
    class Signed:
        value: f[int, 3 - int8]

    assert unpack(Signed, b"\xe0") == Signed(-1)
    assert pack(Signed(-1)) == b"\xe0"


def test_over_wide_value_raises():
    @bitfield(order=BigEndian)
    class Narrow:
        value: f[int, 3]

    with pytest.raises((OverflowError, ValueError, ValidationError)):
        pack(Narrow(0b1000))
