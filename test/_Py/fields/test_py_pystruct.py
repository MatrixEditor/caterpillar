import struct as pystruct

import pytest

from caterpillar.py import (
    BigEndian,
    Context,
    LittleEndian,
    SysNative,
    boolean,
    char,
    float16,
    float32,
    float64,
    int8,
    int16,
    int32,
    int64,
    pack,
    psize,
    pssize,
    uint8,
    uint16,
    uint32,
    uint64,
    unpack,
    void_ptr,
)


def test_integer_formats_sizes_and_endianness():
    cases = [
        (int8, -5, b"\xfb", b"\xfb"),
        (uint8, 250, b"\xfa", b"\xfa"),
        (int16, 0x1234, b"\x34\x12", b"\x12\x34"),
        (uint16, 0x1234, b"\x34\x12", b"\x12\x34"),
        (int32, 0x12345678, b"\x78\x56\x34\x12", b"\x12\x34\x56\x78"),
        (uint32, 0x12345678, b"\x78\x56\x34\x12", b"\x12\x34\x56\x78"),
        (
            int64,
            0x0123456789ABCDEF,
            b"\xef\xcd\xab\x89\x67\x45\x23\x01",
            b"\x01\x23\x45\x67\x89\xab\xcd\xef",
        ),
        (
            uint64,
            0x0123456789ABCDEF,
            b"\xef\xcd\xab\x89\x67\x45\x23\x01",
            b"\x01\x23\x45\x67\x89\xab\xcd\xef",
        ),
    ]
    for field, value, little, big in cases:
        assert field.__size__(Context()) == len(little)
        assert pack(value, field, order=LittleEndian) == little
        assert pack(value, field, order=BigEndian) == big
        assert unpack(field, little, order=LittleEndian) == value
        assert unpack(field, big, order=BigEndian) == value


def test_char_and_boolean_formats():
    assert pack(b"A", char) == b"A"
    assert unpack(char, b"A") == b"A"
    assert pack(False, boolean) == b"\x00"
    assert pack(True, boolean) == b"\x01"
    assert unpack(boolean, b"\x00") is False
    assert unpack(boolean, b"\x01") is True


def test_fixed_array_uses_requested_endianness():
    field = uint16[2]
    assert pack([0x1234, 0x5678], field, order=BigEndian) == b"\x12\x34\x56\x78"
    assert unpack(field, b"\x12\x34\x56\x78", order=BigEndian) == [0x1234, 0x5678]


def test_float_formats():
    assert pack(1.5, float16, order=LittleEndian) == pystruct.pack("<e", 1.5)
    assert pack(1.5, float16, order=BigEndian) == pystruct.pack(">e", 1.5)
    assert unpack(float16, pystruct.pack("<e", 1.5), order=LittleEndian) == pytest.approx(1.5)

    assert pack(3.25, float32, order=LittleEndian) == pystruct.pack("<f", 3.25)
    assert pack(3.25, float32, order=BigEndian) == pystruct.pack(">f", 3.25)
    assert unpack(float32, pystruct.pack("<f", 3.25), order=LittleEndian) == pytest.approx(3.25)

    assert pack(3.25, float64, order=LittleEndian) == pystruct.pack("<d", 3.25)
    assert pack(3.25, float64, order=BigEndian) == pystruct.pack(">d", 3.25)
    assert unpack(float64, pystruct.pack(">d", 3.25), order=BigEndian) == pytest.approx(3.25)


# --------------------------------------------------------------------------- #
# validation and native-only formats
# --------------------------------------------------------------------------- #
def test_packing_wrong_types_raises():
    for field, value in ((uint16, "not an int"), (float32, "not a float"), (char, b"too long")):
        with pytest.raises(pystruct.error):
            pack(value, field)


def test_native_only_formats():
    assert pack(42, pssize, order=SysNative) == pystruct.pack("@n", 42)
    assert unpack(pssize, pystruct.pack("@n", 42), order=SysNative) == 42
    assert pack(42, psize, order=SysNative) == pystruct.pack("@N", 42)
    assert unpack(psize, pystruct.pack("@N", 42), order=SysNative) == 42
    assert pack(0x1000, void_ptr, order=SysNative) == pystruct.pack("@P", 0x1000)
    assert unpack(void_ptr, pystruct.pack("@P", 0x1000), order=SysNative) == 0x1000


def test_native_only_formats_force_native_endian():
    assert pack(42, pssize) == pystruct.pack("@n", 42)
    assert pack(42, psize) == pystruct.pack("@N", 42)
    assert pack(0x1000, void_ptr) == pystruct.pack("@P", 0x1000)


