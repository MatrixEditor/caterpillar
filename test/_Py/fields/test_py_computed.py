import io

from caterpillar.py import Bytes, Computed, Context, f, pack, struct, this, unpack
from caterpillar.types import uint8_t


def test_constant_computed_consumes_and_writes_no_bytes():
    field = Computed(42)
    stream = io.BytesIO(b"ignored")
    assert pack(None, field) == b""
    assert unpack(field, stream) == 42
    assert stream.tell() == 0


def test_lambda_computed():
    field = Computed(lambda context: context._io.tell())
    stream = io.BytesIO(b"abc")
    assert unpack(field, stream) == 0
    assert stream.tell() == 0


def test_computed_size_and_type():
    assert Computed(42).__size__(Context()) == 0
    assert Computed(42).__type__() is int
    assert Computed(lambda context: 42).__type__() is object


def test_this_expression_computed_field_in_struct():
    @struct
    class Format:
        length: uint8_t
        doubled: f[int, Computed(this.length * 2)]
        payload: f[bytes, Bytes(this.length)]

    obj = Format(length=3, doubled=6, payload=b"abc")
    assert unpack(Format, b"\x03abcTAIL") == obj
    assert pack(obj) == b"\x03abc"


def test_lambda_computed_field():
    @struct
    class Format:
        value: uint8_t
        plus_five: f[int, Computed(lambda context: context._obj.value + 5)]

    assert unpack(Format, b"\x07trailing") == Format(7, 12)
