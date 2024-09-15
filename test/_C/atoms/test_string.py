# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar._C import unpack, pack, string, octetstring, pstring
    from caterpillar._C import BIG_ENDIAN as be, u16, u8, cstring

    def test_stringatom_unpack():
        # The string atom works as a basic converter between
        # bytes and unicode objects.
        assert unpack(b"foo", string(3, "utf-8")) == "foo"
        assert unpack(b"foo", string(3)) == "foo"

    def test_stringatom_pack():
        # The string atom works as a basic converter between
        # bytes and unicode objects.
        assert pack("foo", string(3, "utf-8")) == b"foo"

        # TODO:
        # we can even apply the endian here. It will append
        # "-be" or "-le" at the end of the codec string.
        # assert unpack(b"\x00f\x00o\x00o", be + string(3, "utf-16")) == "foo"

    def test_bytesatom_unpack():
        # To parse raw bytes you can use the octetstring, which
        # is basically the C equivalent for caterpillar.py.Bytes
        assert unpack(b"foo", octetstring(3)) == b"foo"
        assert unpack(b"foobar", octetstring(3)[2]) == [b"foo", b"bar"]

    def test_pstringatom_pack():
        # P-Strings or (Pascal-String) are a special case of
        # string atoms where the length of the string is stored
        # in the first byte(s).
        assert pack("foo", pstring(u8, "utf-8")) == b"\x03foo"
        # NOTE that the byteorder operator will be applied to
        # the underlying struct.
        assert pack("bar", be + pstring(u16)) == b"\x00\x03bar"

    def test_pstringatom_unpack():
        # Same applies to parsing data
        assert unpack(b"\x03foo", pstring(u8, "utf-8")) == "foo"
        assert unpack(b"\x00\x03bar", be + pstring(u16, "utf-8")) == "bar"

    def test_cstringatom_pack():
        # C-Strings represent a string with a padding
        s = cstring(..., "utf-8")
        assert pack("foo", s) == b"foo\x00"
        assert pack("bar", cstring(3, "utf-8")) == b"bar"
        assert pack("baz", cstring(u8, "utf-8")) == b"\x04baz\x00"
        assert pack("abc", cstring(4, sep="\x20")) == b"abc\x20"

    def test_cstringatom_unpack():
        assert unpack(b"foo\x00", cstring()) == "foo"
        assert unpack(b"ba\x00r", cstring()) == "ba"
        assert unpack(b"baz\x00", cstring(3)) == "baz"
        assert unpack(b"baz\x00", cstring(4)) == "baz"
        assert unpack(b"\x04baz\x00", cstring(u8)) == "baz"
        assert unpack(b"abc\x20", cstring(4, sep="\x20")) == "abc"
