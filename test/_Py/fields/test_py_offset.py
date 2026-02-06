import pytest

from caterpillar.py import (
    struct,
    pack,
    unpack,
    uint8,
    this,
)

def test_fixed_offset_unpack():
    atom = uint8 @ 4
    data = b"\x00\x00\x00\x00\x42"
    assert unpack(atom, data, as_field=True) == 0x42

def test_dynamic_offset_unpack():
    @struct
    class Format:
        offset: uint8
        data: uint8 @ this.offset

    binary = b"\x04\x00\x00\x00\xAB"
    assert unpack(Format, binary) == Format(offset=4, data=0xAB)

# offset packs do not seem to be working correctly
# These tests show the current behavior

def test_fixed_offset_pack():
    atom = uint8 @ 4
    assert pack(0x42, atom, as_field=True) == b"\x42"

def test_dynamic_offset_pack():
    @struct
    class Format:
        offset: uint8
        data: uint8 @ this.offset

    obj = Format(offset=4, data=0xAB)
    assert pack(obj) == b"\x04\xab"
