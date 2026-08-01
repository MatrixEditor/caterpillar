import enum

import pytest

from caterpillar.py import Enum, InvalidValueError, ValidationError, pack, uint8, unpack


class Color(enum.Enum):
    RED = 1
    BLUE = 2


class Code(enum.IntEnum):
    A = 1
    B = 2


class Perm(enum.IntFlag):
    READ = 1
    WRITE = 2


def test_known_enum_member():
    field = Enum(Color, uint8)
    assert pack(Color.RED, field) == b"\x01"
    assert unpack(field, b"\x01") is Color.RED


def test_intenum_member():
    field = Enum(Code, uint8)
    assert pack(Code.B, field) == b"\x02"
    assert unpack(field, b"\x02") is Code.B


def test_unknown_value_non_strict_returns_raw_int():
    value = unpack(Enum(Color, uint8), b"\x03")
    assert value == 3
    assert type(value) is int


def test_unknown_value_strict_raises():
    with pytest.raises(InvalidValueError):
        unpack(Enum(Color, uint8, strict=True), b"\x03")


def test_pack_raw_int_non_strict_is_allowed():
    field = Enum(Color, uint8)
    assert pack(2, field) == b"\x02"
    assert unpack(field, b"\x02") is Color.BLUE


def test_default_is_used_for_unknown_value():
    assert unpack(Enum(Color, uint8, default=Color.BLUE), b"\xff") is Color.BLUE


def test_intflag_combination():
    field = Enum(Perm, uint8)
    value = Perm.READ | Perm.WRITE
    assert pack(value, field) == b"\x03"
    assert unpack(field, b"\x03") == value


def test_intflag_unknown_bits_return_pseudo_member():
    value = unpack(Enum(Perm, uint8), b"\xff")
    assert value == Perm(0xFF)
    assert isinstance(value, Perm)


# --------------------------------------------------------------------------- #
def test_strict_raw_int_pack_raises():
    with pytest.raises(ValidationError):
        pack(1, Enum(Color, uint8, strict=True))
