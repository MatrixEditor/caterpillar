# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar


if caterpillar.native_support():

    from caterpillar._C import unpack, pack, varint, varint_t
    from caterpillar._C import BIG_ENDIAN as be

    def test_varint_init():
        # The C varint atom implements a variable-length unsigned
        # integer for big-endian AND little-endian encoding. The
        # byteorder operator '+' can be applied as usual.
        assert varint_t(True).little_endian is True
        assert varint_t(False).little_endian is False

        # We can even control the least significant byte using
        # the 'lsb' flag.
        assert varint_t(lsb=True).lsb is True
        assert varint_t(lsb=False).lsb is False

        # These parameters are virible through the representation:
        #  little-endian: <le varint>
        #  big-endian:    <be varint>
        #
        #  little-endian + lsb: <le varint [lsb]>
        #  big-endian + lsb:    <be varint [lsb]>

    def test_varint_pack():
        value = 1024
        # be + varint should result in b'\x88\x00'
        assert pack(value, be + varint) == b"\x88\x00"
        # le + varint should result in b'\x80\x08'
        assert pack(value, varint) == b'\x80\x08'

    def test_varint_unpack():
        value = 1024
        assert unpack(b"\x80\x08", varint) == value
        assert unpack(b"\x88\x00", be + varint) == value

