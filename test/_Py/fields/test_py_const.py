import pytest

from caterpillar.py import unpack, pack, Const, uint8
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
        unpack(field, b"\x24", as_field=True)
