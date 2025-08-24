# pyright: reportInvalidTypeForm=false, reportGeneralTypeIssues=false
import pytest
import enum

from caterpillar.model import (
    Bitfield,
    bitfield,
    NewGroup,
    EndGroup,
    SetAlignment,
    sizeof,
    unpack,
    CharFactory,
    pack,
)
from caterpillar.options import (
    B_GROUP_END,
    B_GROUP_KEEP,
    B_GROUP_NEW,
    B_NO_AUTO_BOOL,
    B_OVERWRITE_ALIGNMENT,
    S_REPLACE_TYPES,
)
from caterpillar.fields import uint16, uint24, uint32, Bytes, uint8
from caterpillar.shared import getstruct


def test_bitfield_syntax__standard():
    # Syntax no. 1
    @bitfield
    class FormatA:
        a: 3 - uint16

    groups = FormatA.__struct__.groups
    assert len(groups) == 1
    assert not groups[0].is_empty()
    # default alignment is 0x08 unless B_OVERWRITE_ALIGNMENT is set
    assert groups[0].bit_count == 0x08
    assert groups[0].entries[0].width == 3


def test_bitfield_syntax__align():
    # Syntax no. 1 + no. 2
    @bitfield
    class FormatA:
        a: 3
        _: 0
        b: 4

    groups = FormatA.__struct__.groups
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
        a: uint16
        b: uint32
        c: uint24

    # just like a @struct definition
    assert sizeof(FormatA) == 2 + 4 + 3


def test_bitfield_syntax__field_factory():
    # syntax no. 4
    @bitfield
    class FormatA:
        a: (uint16, int)  # this won't work
        b: (5 - uint8, str)

    struct = getstruct(FormatA)
    assert struct is not None

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
        a1: (4, str)
        # 2bits converted to Enum
        a2: (2, SimpleEnum)
        # alignment is 8 bits, finalize group and set alignment
        # to 16bits for next group
        _: (0, SetAlignment(16))
        # 10bits entry for current group, then finalize group
        b1: (10, EndGroup)
        # 12bits in new group
        c1: 12

    # We should see exactly three groups here
    groups = FormatA.__struct__.groups
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
        a1: (4, str)  # a1: str
        a2: (2, SimpleEnum)  # a2: SimpleEnum
        _: 0
        b1: Bytes(6)  # b1: bytes

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
        a1: (4, CharFactory)  # a1: str
        a2: (2, SimpleEnum)  # a2: SimpleEnum
        _: 0
        b1: Bytes(6)  # b1: bytes

    # 0b00110100.to_bytes()
    data = b"4" + b"12" * 3
    obj = unpack(FormatA, data)
    assert obj.a1 == "\x03"
    assert obj.a2 == SimpleEnum.B
    assert obj.b1 == b"12" * 3


def test_bitfield__pack():
    @bitfield
    class FormatA:
        a1: 1
        a2: 2
        a3: 3
        _: 0
        b1: uint16

    obj = FormatA(a1=True, a2=3, a3=5, b1=0xFF00)
    # 0b1_11_101_00.to_bytes()
    assert pack(obj) == b"\xf4" + b"\x00\xff"
