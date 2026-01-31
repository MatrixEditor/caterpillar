# Copyright (C) MatrixEditor 2023-2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import ipaddress
import binascii
import re

from typing import Final
from typing_extensions import override

from caterpillar.abc import _ContextLike  # pyright: ignore[reportPrivateUsage]
from .common import Transformer, uint32, UInt, Bytes
from ._base import singleton


@singleton
class IPv4Address(Transformer[ipaddress.IPv4Address, int, ipaddress.IPv4Address, int]):
    """
    A transformer for encoding and decoding IPv4 addresses.
    """

    __slots__: tuple[()] = ()

    def __init__(self) -> None:
        """
        Initialize the IPv4Address transformer.
        """
        super().__init__(uint32)

    @override
    def __type__(self) -> type:
        """
        Get the type associated with the transformer.

        :return: The type associated with the transformer.
        :rtype: type
        """
        return ipaddress.IPv4Address

    @override
    def encode(self, obj: ipaddress.IPv4Address, context: _ContextLike) -> int:
        """
        Encode an IPv4Address object.

        :param ipaddress.IPv4Address obj: The IPv4Address object to encode.
        :param _ContextLike context: The context for encoding.
        :return: The encoded value.
        """
        return obj._ip

    @override
    def decode(self, parsed: int, context: _ContextLike) -> ipaddress.IPv4Address:
        """
        Decode an encoded IPv4 address.

        :param int parsed: The parsed integer value representing the IPv4 address.
        :param _ContextLike context: The context for decoding.
        :return: The decoded IPv4 address.
        """
        return ipaddress.IPv4Address(parsed)


@singleton
class IPv6Address(Transformer[ipaddress.IPv6Address, int, ipaddress.IPv6Address, int]):
    """
    A transformer for encoding and decoding IPv6 addresses.
    """

    __slots__: tuple[()] = ()

    def __init__(self) -> None:
        """
        Initialize the IPv6Address transformer.
        """
        super().__init__(UInt(ipaddress.IPV6LENGTH))

    @override
    def __type__(self) -> type:
        """
        Get the type associated with the transformer.

        :return: The type associated with the transformer.
        :rtype: type
        """
        return ipaddress.IPv6Address

    @override
    def encode(self, obj: ipaddress.IPv6Address, context: _ContextLike) -> int:
        """
        Encode an IPv6Address object.

        :param ipaddress.IPv6Address obj: The IPv6Address object to encode.
        :param _ContextLike context: The context for encoding.
        :return: The encoded value.
        """
        return obj._ip

    @override
    def decode(self, parsed: int, context: _ContextLike) -> ipaddress.IPv6Address:
        """
        Decode an encoded IPv6 address.

        :param int parsed: The parsed integer value representing the IPv6 address.
        :param _ContextLike context: The context for decoding.
        :return: The decoded IPv6 address.
        """
        return ipaddress.IPv6Address(parsed)


class MACAddress(Transformer[str | bytes, bytes, bytes, bytes]):
    """
    A transformer for encoding and decoding MAC addresses.

    :param Optional[str] sep: The separator to use in the MAC address representation.
    """

    DELIMITERS: re.Pattern[bytes] = re.compile(rb"[:-]")

    def __init__(self, sep: str | None = None, encoding: str | None = None) -> None:
        """
        Initialize the MACAddress transformer.

        :param Optional[str] sep: The separator to use in the MAC address representation.
        """
        super().__init__(Bytes(6))
        self.sep: str = sep or ":"
        self.encoding: str = encoding or "utf-8"

    @override
    def encode(self, obj: str | bytes, context: _ContextLike) -> bytes:
        """
        Encode a MAC address.

        :param Union[str, bytes] obj: The MAC address to encode.
        :param _ContextLike context: The context for encoding.
        :return: The encoded value.
        """
        if isinstance(obj, str):
            obj = obj.encode(self.encoding)

        # replace unnecessary characters
        mac = re.sub(MACAddress.DELIMITERS, b"", obj)
        return binascii.unhexlify(mac)

    @override
    def decode(self, parsed: bytes, context: _ContextLike) -> bytes:
        """
        Decode an encoded MAC address.

        :param bytes parsed: The parsed bytes representing the MAC address.
        :param _ContextLike context: The context for decoding.
        :return: The decoded MAC address.
        """
        return binascii.b2a_hex(parsed, self.sep)


#: shortcut for default MAC address format
MAC: Final[MACAddress] = MACAddress()
