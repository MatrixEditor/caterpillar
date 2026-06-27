import ipaddress

import pytest

from caterpillar.py import IPv4Address, IPv6Address, pack, unpack


def test_zero_and_broadcast_boundaries_use_four_bytes():
    assert pack(ipaddress.IPv4Address("0.0.0.0"), IPv4Address) == b"\x00\x00\x00\x00"
    assert unpack(IPv4Address, b"\x00\x00\x00\x00") == ipaddress.IPv4Address("0.0.0.0")
    assert pack(ipaddress.IPv4Address("255.255.255.255"), IPv4Address) == b"\xff" * 4
    assert unpack(IPv4Address, b"\xff" * 4) == ipaddress.IPv4Address("255.255.255.255")


def test_ipaddress_object_pack_unpack():
    address = ipaddress.IPv4Address("192.0.2.129")

    assert unpack(IPv4Address, pack(address, IPv4Address)) == address


def test_ipv4_object_packs_to_network_order():
    assert pack(ipaddress.IPv4Address("1.2.3.4"), IPv4Address) == b"\x01\x02\x03\x04"


def test_ipv4_unpack():
    assert unpack(IPv4Address, b"\x01\x02\x03\x04") == ipaddress.IPv4Address("1.2.3.4")


def test_ipv4_pack_string():
    assert pack("1.2.3.4", IPv4Address) == b"\x01\x02\x03\x04"


def test_ipv4_invalid():
    with pytest.raises(ValueError):
        pack("999.1.1.1", IPv4Address)


def test_ipv6_use_sixteen_bytes():
    unspecified = ipaddress.IPv6Address("::")
    all_ones = ipaddress.IPv6Address("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")

    assert pack(unspecified, IPv6Address) == b"\x00" * 16
    assert unpack(IPv6Address, b"\x00" * 16) == unspecified
    assert pack(all_ones, IPv6Address) == b"\xff" * 16
    assert unpack(IPv6Address, b"\xff" * 16) == all_ones


def test_ipv6_pack_unpack():
    for address in [
        ipaddress.IPv6Address("2001:db8::1"),
        ipaddress.IPv6Address("::ffff:192.0.2.128"),
    ]:
        assert unpack(IPv6Address, pack(address, IPv6Address)) == address


def test_ipv6__object_packs_to_network_order():
    address = ipaddress.IPv6Address("2001:db8::1")

    assert pack(address, IPv6Address) == address.packed


def test_ipv6_unpack():
    address = ipaddress.IPv6Address("::ffff:192.0.2.128")

    assert unpack(IPv6Address, address.packed) == address


def test_compressed_text_packs_like_ipaddress_object():
    address = ipaddress.IPv6Address("2001:db8::1")

    assert pack("2001:db8::1", IPv6Address) == address.packed


def test_invalid_ipv6():
    with pytest.raises(ValueError):
        pack("not-an-ipv6-address", IPv6Address)
