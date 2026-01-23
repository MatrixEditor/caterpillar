import pytest

from caterpillar.py import ValidationError, identity, padding, pack, unpack, Padding


def test_py_padding():
    # the global variable can be used to place a default padding
    # with null bytes
    assert padding.fill == b"\x00"
    assert padding.strict is False

    # it corresponds to the default constructor arguments
    assert Padding().fill == b"\x00"


def test_py_padding_pack():
    # packing is done without an inpput argument
    assert pack(None, padding) == b"\x00"


def test_py_padding_custom_pack():
    # is is also possible to specify an arbitrary-length padding
    pad = Padding(b"AB")[10]
    assert pack(None, pad) == b"AB" * 10


def test_py_padding_unpack():
    # parsing also returns nothing
    assert unpack(padding, b"\x00") is None


def test_py_padding_unpack_strict():
    # There is also a strict mode that checks the data read
    # from the stream afterwards
    pad = Padding(strict=True)
    with pytest.raises(ValidationError):
        _ = unpack(pad, b"\x01")


def test_py_padding_custom_unpack_strict():
    pad = Padding(fill=b"AB", strict=True)
    with pytest.raises(ValidationError):
        _ = unpack(pad, b"\x01\x02\x03")


def test_py_padding_context_length():
    pad = padding[identity(10)] # always 10
    assert pack(None, pad) == b"\x00" * 10
