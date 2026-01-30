import pytest

from caterpillar.py import ConstBytes, Invisible, f, struct, unpack, pack, Const, uint8
from caterpillar.exception import ValidationError


def test_const_pack():
    field = Const(42, uint8)
    # the input value will be ignored
    assert pack(None, field, as_field=True) == b"\x2a"


def test_const_unpack():
    field = Const(42, uint8)
    # output value will be the constant if parsed matches
    assert unpack(field, b"\x2a", as_field=True) == 42


def test_const_unpack_error():
    field = Const(42, uint8)
    with pytest.raises(ValidationError):
        # must raise an exception
        _ = unpack(field, b"\x24", as_field=True)


def test_const_bytes_pack():
    value = b"A" * 100
    field = ConstBytes(value)
    # same as Const(...), we use None as input
    assert pack(None, field) == value


def test_const_bytes_unpack():
    value = b"A" * 100
    field = ConstBytes(value)
    # same as Const(...), we use None as input
    assert unpack(field, value) == value


def test_const_bytes_structdef():
    value = b"B" * 42

    @struct
    class Format:
        # a constant value will be replaced with ConstBytes
        const: f[bytes, value] = Invisible()

    # no arguments needed
    obj = Format()
    assert obj.const == value
    assert pack(obj) == value
    assert unpack(Format, value).const == value


def test_const_str_structdef():
    # constant strings are allowed too
    value = "A" * 42

    @struct
    class Format:
        # value will be replaced with ConstString
        const: f[str, value] = Invisible()

    obj = Format()
    assert obj.const == value
    assert pack(obj) == value.encode()
    assert unpack(Format, value.encode()).const == value
