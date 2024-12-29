from enum import Enum as PyEnum

from caterpillar.py import pack, unpack, Enum as CpEnum, uint8, Bytes


class Color(PyEnum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Command(PyEnum):
    START = b"ST"
    END = b"EN"
    UNKNOWN = b"??"


def test_py_enum_pack():
    cp_enum = CpEnum(Color, uint8)
    assert pack(Color.RED, cp_enum, as_field=True)


def test_py_enum_unpack():
    cp_enum = CpEnum(Color, uint8)
    assert unpack(cp_enum, b"\x03", as_field=True) == Color.BLUE


def test_py_enum_custom():
    cp_enum = CpEnum(Command, Bytes(2))
    assert unpack(cp_enum, b"EN", as_field=True) == Command.END
    assert pack(Command.START, cp_enum, as_field=True) == b"ST"
