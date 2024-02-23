# file: test_enum
# All tests conducted here try to show the limitations of the
# enum integraton. They also show what you can do with enums
# and how they can be used.
import enum

from caterpillar.fields import uint8, Enum, String, Bytes
from caterpillar.shortcuts import struct, BigEndian

from _utils import _test_pack, _test_unpack


###############################################################################
# default enum definition (IntEnum)
###############################################################################
class Enum_Default(enum.IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4


@struct
class Format_Default:
    field: Enum(Enum_Default, uint8)
    field_with_default: Enum(Enum_Default, uint8) = Enum_Default.A


def test_enum_default_pack():
    _test_pack(Format_Default(Enum_Default.B), b"\x01\x00")
    _test_pack(Format_Default(Enum_Default.C, Enum_Default.D), b"\x02\x03")


def test_enum_default_unpack():
    _test_unpack(
        Format_Default, b"\x04", Format_Default(Enum_Default.E, Enum_Default.A)
    )
    _test_unpack(
        Format_Default, b"\x03\x02", Format_Default(Enum_Default.D, Enum_Default.C)
    )


###############################################################################
# enum with struct (string enum)
###############################################################################
class Enum_WithStruct(enum.StrEnum):
    __struct__ = String(3)

    A = "aAa"
    B = "bBb"
    C = "cCc"
    D = "dDd"


@struct
class Format_WithStruct:
    field: Enum_WithStruct
    field_wd: Enum_WithStruct = Enum_WithStruct.A  # wd := with default


def test_enum_with_struct_pack():
    _test_pack(Format_WithStruct(Enum_WithStruct.B), b"bBbaAa")
    _test_pack(Format_WithStruct(Enum_WithStruct.C, Enum_WithStruct.D), b"cCcdDd")


def test_enum_with_struct_unpack():
    _test_unpack(
        Format_WithStruct,
        b"dDd",
        Format_WithStruct(Enum_WithStruct.D, Enum_WithStruct.A),
    )
    _test_unpack(
        Format_WithStruct,
        b"dDdcCc",
        Format_WithStruct(Enum_WithStruct.D, Enum_WithStruct.C),
    )


###############################################################################
# enum in array (bytes enum)
###############################################################################
class Enum_Array(enum.Enum):
    A = b"a..a"
    B = b"b..b"
    C = b"c..c"
    D = b"d..d"


@struct(order=BigEndian)
class Format_Array:
    # here, we can't use <Class>[...], because the enum class has another
    # implementation for this special operation.
    field: Enum(Enum_Array, Bytes(4))[uint8::]


def test_enum_array_pack():
    _test_pack(Format_Array([Enum_Array.B, Enum_Array.C]), b"\x02b..bc..c")


def test_enum_array_unpack():
    _test_unpack(
        Format_Array,
        b"\x03a..ad..db..b",
        Format_Array([Enum_Array.A, Enum_Array.D, Enum_Array.B]),
    )
