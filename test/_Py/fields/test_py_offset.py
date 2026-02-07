import pytest

from caterpillar.py import (
    f,
    struct,
    pack,
    unpack,
    uint8,
    this,
)


def test_fixed_offset_unpack():
    atom = uint8 @ 4
    data = b"\x00\x00\x00\x00\x42"
    assert unpack(atom, data) == 0x42
    # or directly:
    assert atom.from_bytes(data) == 0x42
    # or using inline syntax
    assert atom << data == 0x42


def test_dynamic_offset_unpack():
    @struct
    class Format:
        offset: f[int, uint8]
        data: f[int, uint8 @ this.offset]

    binary = b"\x04\x00\x00\x00\xab"
    assert unpack(Format, binary) == Format(offset=4, data=0xAB)


def test_fixed_offset_pack_invalid():
    atom = uint8 @ 4
    # this behavior was fixed in #58
    assert pack(0x42, atom) != b"\x42"
    assert pack(0x42, atom) == b"\x00\x00\x00\x00\x42"


def test_dynamic_offset_pack():
    @struct
    class Format:
        offset: f[int, uint8]
        data: f[int, uint8 @ this.offset]

    obj = Format(offset=4, data=0xAB)
    assert pack(obj) == b"\x04\x00\x00\x00\xab"
