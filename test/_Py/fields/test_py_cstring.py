import io

import pytest

from caterpillar.py import CString, pack, unpack, ValidationError


def test_fixed_cstring():
    c = CString(6)
    assert pack("Hello", c) == b"Hello\x00"
    assert unpack(c, b"Hello\x00") == "Hello"


def test_fixed_pads_short_value():
    c = CString(8)
    assert pack("Hi", c) == b"Hi\x00\x00\x00\x00\x00\x00"
    assert unpack(c, b"Hi\x00\x00\x00\x00\x00\x00") == "Hi"


def test_fixed_too_long_raises():
    c = CString(4)
    with pytest.raises(ValidationError):
        _ = pack("toolong", c)


def test_fixed_empty_string():
    c = CString(4)
    assert pack("", c) == b"\x00\x00\x00\x00"
    assert unpack(c, b"\x00\x00\x00\x00") == ""


def test_exact_fill_drops_terminator():
    c = CString(5)
    assert pack("Hello", c) == b"Hello"  # note: no trailing \x00
    assert unpack(c, b"Hello") == "Hello"


def test_greedy_cstring():
    c = CString()
    assert pack("Hi", c) == b"Hi\x00"
    assert unpack(c, b"Hi\x00trailing") == "Hi"


def test_greedy_empty():
    c = CString()
    assert pack("", c) == b"\x00"
    assert unpack(c, b"\x00") == ""


def test_greedy_non_seekable_stream():
    # greedy unpack must also work byte-by-byte on a non-seekable stream
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

    stream = NonSeekable(b"abc\x00xyz")
    assert unpack(CString(), stream) == "abc"


def test_custom_pad_char():
    c = CString(6, pad=" ")
    assert pack("Hi", c) == b"Hi    "
    assert unpack(c, b"Hi    ") == "Hi"


def test_multibyte_capacity_is_in_bytes():
    # length is measured in *bytes*, not characters.
    c = CString(6, encoding="utf-8")
    assert pack("\u00e9\u00e9\u00e9", c) == "\u00e9\u00e9\u00e9".encode("utf-8")
    # 3 x 2-byte chars exactly fills 6 bytes -> no terminator
    assert unpack(c, "\u00e9\u00e9\u00e9".encode("utf-8")) == "\u00e9\u00e9\u00e9"


def test_multibyte_overflow_raises():
    c = CString(4, encoding="utf-8")
    with pytest.raises(ValidationError):
        pack("\u00e9\u00e9\u00e9", c)  # 6 bytes > 4


def test_zero_length_is_not_greedy():
    c = CString(0)
    # a 0-length field should pack to b"" (or raise), never become greedy
    assert c.length == 0


def test_array_of_cstrings():
    seq = CString()[2]
    assert unpack(seq, b"a\x00bb\x00") == ["a", "bb"]
