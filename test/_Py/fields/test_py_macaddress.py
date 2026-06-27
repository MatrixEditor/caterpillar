import binascii

import pytest

from caterpillar.py import MACAddress, ValidationError, pack, unpack


RAW = b"\xaa\xbb\xcc\xdd\xee\xff"


def test_mac_basic_pack():
    mac = MACAddress()

    assert pack("aa:bb:cc:dd:ee:ff", mac) == RAW
    assert pack("AA:BB:CC:DD:EE:FF", mac) == RAW
    assert pack("aa-bb-cc-dd-ee-ff", mac) == RAW
    assert pack("aabbccddeeff", mac) == RAW


def test_unpack_uses_default_and_custom_separators():
    assert unpack(MACAddress(), RAW) == "aa:bb:cc:dd:ee:ff"
    assert unpack(MACAddress("-"), RAW) == "aa-bb-cc-dd-ee-ff"


def test_mac_canonicalizes_case_and_separator():
    mac = MACAddress()

    assert unpack(mac, pack("AA-BB-CC-DD-EE-FF", mac)) == "aa:bb:cc:dd:ee:ff"


def test_invalid_mac():
    mac = MACAddress()

    with pytest.raises(ValidationError):
        pack("aa:bb:cc:dd:ee", mac)
    with pytest.raises(ValidationError):
        pack("aa:bb:cc:dd:ee:ff:00", mac)
    with pytest.raises(binascii.Error):
        pack("gg:bb:cc:dd:ee:ff", mac)


def test_unpack_returns_text_string():
    assert unpack(MACAddress(), RAW) == "aa:bb:cc:dd:ee:ff"


def test_dotted_notation_packs_to_six_bytes():
    assert pack("aabb.ccdd.eeff", MACAddress()) == RAW


def test_raw_six_byte_value_packs_unchanged():
    assert pack(RAW, MACAddress()) == RAW
