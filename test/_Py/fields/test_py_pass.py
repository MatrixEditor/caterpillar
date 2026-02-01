from caterpillar.py import (
    struct,
    unpack,
    pack,
    Pass,
)
from caterpillar.types import pass_t


def test_py_pass_init():
    # special field: Pass does nothing (may be useful in switch statements)
    field = Pass
    # 'Pass' is a sigleton
    assert field


def test_py_pass_pack():
    # will write nothing to the stream.
    field = Pass
    assert pack(None, field) == b""


def test_py_pass_unpack():
    # parsing does not modify the underlying stream
    field = Pass
    assert unpack(field, b"") is None


def test_py_pass_structdef():
    # There are two ways to define 'Pass' in a struct:
    #   1. either using the pre-defined pass_t type, or
    #   2. directly using 'Pass'
    @struct
    class Format:
        novalue: pass_t
        # or
        # novalue: Pass

    obj = Format(novalue=None)
    assert obj.novalue is None
    assert pack(obj) == b""
    assert unpack(Format, b"") == obj
