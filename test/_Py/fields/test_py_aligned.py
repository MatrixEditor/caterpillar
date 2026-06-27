import io

import pytest

from caterpillar.py import Aligned, Bytes, f, pack, struct, this, uint8, uint16, uint32, unpack
from caterpillar.types import uint8_t


def test_after_alignment_pads_to_boundary_and_consumes_padding():
    field = Aligned(uint16, 4, after=True)
    assert pack(0x1234, field) == b"\x34\x12\x00\x00"

    stream = io.BytesIO(b"\x34\x12\x00\x00\xff")
    assert unpack(field, stream) == 0x1234
    assert stream.tell() == 4
    assert stream.read() == b"\xff"


def test_after_alignment_already_aligned_writes_no_padding():
    field = Aligned(uint32, 4, after=True)
    assert pack(0x12345678, field) == b"\x78\x56\x34\x12"

    stream = io.BytesIO(b"\x78\x56\x34\x12\xff")
    assert unpack(field, stream) == 0x12345678
    assert stream.tell() == 4
    assert stream.read() == b"\xff"


def test_custom_filler_is_written_and_validated():
    field = Aligned(uint16, 4, after=True, filler="P")
    assert pack(0x1234, field) == b"\x34\x12PP"
    assert unpack(field, b"\x34\x12PP") == 0x1234
    with pytest.raises(ValueError):
        unpack(field, b"\x34\x12P\x00")


def test_before_alignment_in_struct():
    @struct
    class Format:
        lead: uint8_t
        value: f[int, Aligned(uint16, 4, before=True)]
        tail: uint8_t

    obj = Format(0xAA, 0x1234, 0xBB)
    data = b"\xaa\x00\x00\x00\x34\x12\xbb"
    assert pack(obj) == data
    assert unpack(Format, data) == obj


def test_context_driven_inner_length_alignment():
    @struct
    class Format:
        length: uint8
        payload: f[bytes, Aligned(Bytes(this.length), 4, after=True, filler="P")]
        tail: uint8

    obj = Format(2, b"ab", 0xEE)
    assert pack(obj) == b"\x02abP\xee"
    assert unpack(Format, b"\x02abP\xee") == obj


def test_dynamic_alignment_from_context():
    @struct
    class Format:
        alignment: uint8
        value: f[int, Aligned(uint8, this.alignment, after=True)]
        tail: uint8

    obj = Format(4, 0xAA, 0xBB)
    assert pack(obj) == b"\x04\xaa\x00\x00\xbb"
    assert unpack(Format, b"\x04\xaa\x00\x00\xbb") == obj


def test_invalid_alignment_raises_when_used():
    with pytest.raises(ValueError):
        pack(1, Aligned(uint8, 0, after=True))
    with pytest.raises(ValueError):
        pack(1, Aligned(uint8, 3, after=True))


# --------------------------------------------------------------------------- #
# documented inconsistencies (xfail)
# --------------------------------------------------------------------------- #
def test_aligned_static_invalid_alignment():
    with pytest.raises(ValueError):
        Aligned(uint8, 0, after=True)
    with pytest.raises(ValueError):
        Aligned(uint8, 3, after=True)


def test_aligned_invalid_filler():
    with pytest.raises(ValueError):
        Aligned(uint8, 4, after=True, filler=256)
    with pytest.raises(ValueError):
        Aligned(uint8, 4, after=True, filler=-1)
