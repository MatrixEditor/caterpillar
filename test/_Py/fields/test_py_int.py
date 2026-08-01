import pytest

from caterpillar.py import BigEndian, Int, LittleEndian, ValidationError, pack, unpack


# --------------------------------------------------------------------------- #
# byte-aligned arbitrary widths
# --------------------------------------------------------------------------- #
def test_int24_signed_boundaries_little_endian():
    field = Int(24)
    assert pack(-(2**23), field, order=LittleEndian) == b"\x00\x00\x80"
    assert pack(2**23 - 1, field, order=LittleEndian) == b"\xff\xff\x7f"
    assert unpack(field, b"\x00\x00\x80", order=LittleEndian) == -(2**23)
    assert unpack(field, b"\xff\xff\x7f", order=LittleEndian) == 2**23 - 1


def test_int24_big_endian_roundtrip():
    field = Int(24)
    assert pack(0x010203, field, order=BigEndian) == b"\x01\x02\x03"
    assert pack(-2, field, order=BigEndian) == b"\xff\xff\xfe"
    assert unpack(field, b"\x01\x02\x03", order=BigEndian) == 0x010203
    assert unpack(field, b"\xff\xff\xfe", order=BigEndian) == -2


def test_int24_overflow_raises():
    field = Int(24)
    for value in (-(2**23) - 1, 2**23):
        with pytest.raises(OverflowError):
            pack(value, field)


def test_int24_short_read_raises_validation_error():
    with pytest.raises(ValidationError):
        unpack(Int(24), b"\x00\x00")


def test_one_bit_int_uses_storage_instead_of_zero_bytes():
    assert Int(1).__size__({}) == 1


def test_fifteen_bit_signed_boundaries():
    #  non-byte-aligned widths should keep their bytes
    field = Int(15)
    assert pack(2**14 - 1, field, order=BigEndian) == b"\x3f\xff"
    assert pack(-(2**14), field, order=BigEndian) == b"\x40\x00"


def test_zero_bit_int_is_rejected():
    # zero-bit integer widths are rejected
    with pytest.raises(ValueError):
        Int(0)
