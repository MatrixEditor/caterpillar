import io

from caterpillar.py import RelativePointer, int8, pack, struct, uint8, unpack
from caterpillar.types import uint8_t


@struct
class Target:
    value: uint8_t


def test_unpack_uses_pointer_start_as_relative_base():
    stream = io.BytesIO(b"XX\x02!\xab")
    stream.seek(2)

    ptr = unpack(RelativePointer(uint8, Target), stream)

    assert int(ptr) == 2
    assert ptr.base == 2
    assert ptr.absolute == 4
    assert ptr.obj == Target(0xAB)
    assert stream.tell() == 3


def test_signed_relative_pointer_can_point_backward():
    stream = io.BytesIO(b"\x00\xab\x00\xfe")
    stream.seek(3)

    ptr = unpack(RelativePointer(int8, Target), stream)

    assert int(ptr) == -2
    assert ptr.base == 3
    assert ptr.absolute == 1
    assert ptr.obj == Target(0xAB)
    assert stream.tell() == 4


def test_zero_relative_pointer_at_start_is_null():
    ptr = unpack(RelativePointer(uint8, Target), b"\x00\xab")

    assert int(ptr) == 0
    assert ptr.base == 0
    assert ptr.absolute == 0
    assert ptr.obj is None


def test_pack_plain_integer_writes_relative_offset_field():
    assert pack(2, RelativePointer(uint8, Target)) == b"\x02"


def test_zero_relative_pointer_is_null_even_when_field_not_at_zero():
    stream = io.BytesIO(b"XX\x00\xab")
    stream.seek(2)

    ptr = unpack(RelativePointer(uint8, Target), stream)

    assert int(ptr) == 0
    assert ptr.base == 2
    assert ptr.absolute == 2
    assert ptr.obj is None
