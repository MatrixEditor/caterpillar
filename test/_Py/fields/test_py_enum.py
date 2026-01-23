from enum import Enum as PyEnum, IntFlag as PyIntFlag

import pytest

from caterpillar.py import (
    ENUM_STRICT,
    InvalidValueError,
    pack,
    unpack,
    Enum as CpEnum,
    uint8,
    Bytes,
)


class Color(PyEnum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Command(PyEnum):
    START = b"ST"
    END = b"EN"
    UNKNOWN = b"??"


class BitEnum(PyIntFlag):
    A = 1 << 0
    B = 1 << 1
    C = 1 << 2


def test_py_enum_pack():
    cp_enum = CpEnum(Color, uint8)
    assert pack(Color.RED, cp_enum)


def test_py_enum_unpack():
    cp_enum = CpEnum(Color, uint8)
    assert unpack(cp_enum, b"\x03") == Color.BLUE


def test_py_enum_custom():
    cp_enum = CpEnum(Command, Bytes(2))
    assert unpack(cp_enum, b"EN") == Command.END
    assert pack(Command.START, cp_enum) == b"ST"


def test_py_enum_intflag():
    field = CpEnum(BitEnum, uint8)
    assert unpack(field, b"\x01") == BitEnum.A
    assert unpack(field, b"\x03") == BitEnum.A | BitEnum.B
    assert pack(BitEnum.A, field) == b"\x01"


def test_py_enum_strict():
    field = CpEnum(Color, uint8) | ENUM_STRICT
    with pytest.raises(InvalidValueError):
        _ = unpack(field, b"\x04")

    field ^= ENUM_STRICT
    assert unpack(field, b"\x04") == 4