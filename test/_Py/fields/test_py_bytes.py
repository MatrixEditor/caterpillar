import io

import pytest

from caterpillar.py import Bytes, ValidationError, f, pack, struct, this, unpack
from caterpillar.types import uint8_t


class NonSeekable(io.RawIOBase):
    def __init__(self, data):
        self._data = data
        self._pos = 0

    def readable(self):
        return True

    def seekable(self):
        return False

    def read(self, n=-1):
        if n is None or n < 0:
            n = len(self._data) - self._pos
        chunk = self._data[self._pos : self._pos + n]
        self._pos += len(chunk)
        return chunk


def test_bytes_fixed():
    field = Bytes(4)
    assert pack(b"data", field) == b"data"
    assert unpack(field, b"data") == b"data"


def test_fixed_zero_length_does_not_consume_stream():
    stream = io.BytesIO(b"tail")
    assert unpack(Bytes(0), stream) == b""
    assert stream.tell() == 0
    assert pack(b"", Bytes(0)) == b""


def test_fixed_requires_exact_length_on_pack():
    field = Bytes(4)
    with pytest.raises(ValidationError):
        pack(b"abc", field)
    with pytest.raises(ValidationError):
        pack(b"abcde", field)


def test_fixed_unpack_short_input_raises():
    with pytest.raises(ValidationError):
        unpack(Bytes(4), b"abc")


# --------------------------------------------------------------------------- #
# greedy
# --------------------------------------------------------------------------- #
def test_bytes_greedy():
    field = Bytes(...)
    assert pack(b"payload", field) == b"payload"
    assert unpack(field, b"payload") == b"payload"


def test_greedy_empty_input():
    assert pack(b"", Bytes(...)) == b""
    assert unpack(Bytes(...), b"") == b""


def test_greedy_non_seekable_stream():
    stream = NonSeekable(b"abcdef")
    assert unpack(Bytes(...), stream) == b"abcdef"


def test_context_length_via_this():
    @struct
    class Packet:
        length: uint8_t
        payload: f[bytes, Bytes(this.length)]

    obj = Packet(3, b"abc")
    assert pack(obj) == b"\x03abc"

    parsed = unpack(Packet, b"\x03abc")
    assert parsed.length == 3
    assert parsed.payload == b"abc"


def test_array_of_bytes_fields():
    seq = Bytes(2)[3]
    assert pack([b"ab", b"cd", b"ef"], seq) == b"abcdef"
    assert unpack(seq, b"abcdef") == [b"ab", b"cd", b"ef"]
