import io

import pytest

from caterpillar.py import (
    DynamicSizeError,
    Padded,
    Padding,
    PostPad,
    PrePad,
    ValidationError,
    constval,
    f,
    pack,
    padding,
    sizeof,
    struct,
    this,
    uint8,
    uint16,
    unpack,
)
from caterpillar.types import uint8_t


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
    pad = padding[constval(10)]  # always 10
    assert pack(None, pad) == b"\x00" * 10


def test_py_padded_static_pre_and_post_roundtrip():
    field = Padded(uint8, before=2, after=3)

    assert pack(0xAA, field) == b"\x00\x00\xaa\x00\x00\x00"
    assert unpack(field, b"\x00\x00\xaa\x00\x00\x00") == 0xAA


def test_py_padded_custom_fill_repeats_and_truncates_to_byte_length():
    field = Padded(uint8, before=5, after=3, fill=b"AB")

    assert pack(0xCC, field) == b"ABABA\xccABA"
    assert unpack(field, b"12345\xcc678") == 0xCC


def test_py_padded_strict_validates_fill():
    field = Padded(uint8, before=2, after=2, fill=0xFF, strict=True)

    assert unpack(field, b"\xff\xff\x01\xff\xff") == 1
    with pytest.raises(ValidationError):
        _ = unpack(field, b"\xff\x00\x01\xff\xff")
    with pytest.raises(ValidationError):
        _ = unpack(field, b"\xff\xff\x01\xff")


def test_py_padded_context_length():
    @struct
    class Format:
        before: uint8_t
        after: uint8_t
        value: f[int, Padded(uint8, before=this.before, after=this.after, fill=0x50)]

    obj = Format(2, 3, 0xAA)
    data = b"\x02\x03PP\xaaPPP"

    assert pack(obj) == data
    assert unpack(Format, data) == obj


def test_py_padded_invalid_resolved_lengths():
    with pytest.raises(ValueError):
        _ = pack(1, Padded(uint8, before=-1))

    with pytest.raises(ValueError):
        _ = pack(1, Padded(uint8, after=constval("bad")))


def test_py_padded_sizeof_static_and_dynamic():
    assert sizeof(Padded(uint16, before=2, after=4)) == 8

    with pytest.raises(DynamicSizeError):
        _ = sizeof(Padded(uint16, after=this.amount))


def test_py_padded_prepad_postpad():
    direct = PostPad(2, fill=0xCC)(PrePad(1, fill=0xAA)(uint8))
    slash = uint8 / PrePad(1, fill=0xAA) / PostPad(2, fill=0xCC)

    assert pack(0x11, direct) == b"\xaa\x11\xcc\xcc"
    assert pack(0x11, slash) == b"\xaa\x11\xcc\xcc"
    assert unpack(direct, b"\xaa\x11\xcc\xcc") == 0x11
    assert unpack(slash, b"\xaa\x11\xcc\xcc") == 0x11


def test_py_padded_preserves_stream_position():
    field = uint8 / PostPad(2)
    stream = io.BytesIO(b"\x01\x00\x00\xff")

    assert unpack(field, stream) == 1
    assert stream.tell() == 3
    assert stream.read() == b"\xff"
