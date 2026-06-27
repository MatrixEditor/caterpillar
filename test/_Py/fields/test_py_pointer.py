import io

import pytest

from caterpillar.py import Pointer, StructException, pack, pointer, struct, uint8, unpack


@struct
class Target:
    value: uint8


class NonSeekable(io.BytesIO):
    def seekable(self):
        return False

    def seek(self, *args, **kwargs):
        raise io.UnsupportedOperation("no seek")


# --------------------------------------------------------------------------- #
# unpacking
# --------------------------------------------------------------------------- #
def test_unpack_follows_absolute_offset_and_restores_stream_position():
    stream = io.BytesIO(b"\x02\x00\xab\xcc")

    ptr = unpack(Pointer(uint8, Target), stream)

    assert int(ptr) == 2
    assert ptr.obj == Target(0xAB)
    assert stream.tell() == 1


def test_zero_pointer_is_null_and_does_not_parse_model():
    stream = io.BytesIO(b"\x00\xab")

    ptr = unpack(Pointer(uint8, Target), stream)

    assert int(ptr) == 0
    assert ptr.obj is None
    assert stream.tell() == 1


def test_pointer_without_model_does_not_seek():
    stream = NonSeekable(b"\x02\x00\xab")
    ptr = unpack(Pointer(uint8), stream)

    assert int(ptr) == 2
    assert ptr.obj is None


# --------------------------------------------------------------------------- #
# packing
# --------------------------------------------------------------------------- #
def test_pack_plain_integer_writes_only_offset_field():
    assert pack(2, Pointer(uint8, Target)) == b"\x02"


def test_out_of_range_target_returns_pointer():
    ptr = unpack(Pointer(uint8, Target), b"\xff\xaa\xbb")
    assert int(ptr) == 255
    assert ptr.obj is None


def test_pack_pointer_object_writes_pointed_to_model_at_offset():
    # pointer packing should write the pointed-to .obj at its offset.
    ptr = pointer(2)
    ptr.obj = Target(0xAB)

    assert pack(ptr, Pointer(uint8, Target)) == b"\x02\x00\xab"


def test_non_seekable_stream_with_model_raises_struct_exception():
    with pytest.raises(StructException):
        unpack(Pointer(uint8, Target), NonSeekable(b"\x02\x00\xab"))
