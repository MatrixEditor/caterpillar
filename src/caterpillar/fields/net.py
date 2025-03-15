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

from typing import Union, Any, Optional


from caterpillar.abc import _ContextLike
from .common import Transformer, uint32, UInt, Bytes
from ._base import singleton


@singleton
class IPv4Address(Transformer):
    """
    A transformer for encoding and decoding IPv4 addresses.
    """

    __slots__ = ()

    def __init__(self) -> None:
        """
        Initialize the IPv4Address transformer.
        """
        super().__init__(uint32)

    def __type__(self) -> type:
        """
        Get the type associated with the transformer.

        :return: The type associated with the transformer.
        :rtype: type
        """
        return ipaddress.IPv4Address

    def encode(self, obj: ipaddress.IPv4Address, context: _ContextLike) -> Any:
        """
        Encode an IPv4Address object.

        :param ipaddress.IPv4Address obj: The IPv4Address object to encode.
        :param _ContextLike context: The context for encoding.
        :return: The encoded value.
        """
        # pylint: disable-next=protected-access
        return obj._ip

    def decode(self, parsed: int, context: _ContextLike) -> ipaddress.IPv4Address:
        """
        Decode an encoded IPv4 address.

        :param int parsed: The parsed integer value representing the IPv4 address.
        :param _ContextLike context: The context for decoding.
        :return: The decoded IPv4 address.
        """
        return ipaddress.IPv4Address(parsed)


@singleton
class IPv6Address(Transformer):
    """
    A transformer for encoding and decoding IPv6 addresses.
    """

    __slots__ = ()

    def __init__(self) -> None:
        """
        Initialize the IPv6Address transformer.
        """
        super().__init__(UInt(ipaddress.IPV6LENGTH))

    def __type__(self) -> type:
        """
        Get the type associated with the transformer.

        :return: The type associated with the transformer.
        :rtype: type
        """
        return ipaddress.IPv6Address

    def encode(self, obj: ipaddress.IPv6Address, context: _ContextLike) -> Any:
        """
        Encode an IPv6Address object.

        :param ipaddress.IPv6Address obj: The IPv6Address object to encode.
        :param _ContextLike context: The context for encoding.
        :return: The encoded value.
        """
        # pylint: disable-next=protected-access
        return obj._ip

    def decode(self, parsed: int, context: _ContextLike) -> ipaddress.IPv6Address:
        """
        Decode an encoded IPv6 address.

        :param int parsed: The parsed integer value representing the IPv6 address.
        :param _ContextLike context: The context for decoding.
        :return: The decoded IPv6 address.
        """
        return ipaddress.IPv6Address(parsed)


class MACAddress(Transformer):
    """
    A transformer for encoding and decoding MAC addresses.

    :param Optional[str] sep: The separator to use in the MAC address representation.
    """

    DELIMITERS = re.compile(rb"[:-]")

    def __init__(self, sep: Optional[str] = None) -> None:
        """
        Initialize the MACAddress transformer.

        :param Optional[str] sep: The separator to use in the MAC address representation.
        """
        super().__init__(Bytes(6))
        self.sep = sep or ":"

    def encode(self, obj: Union[str, bytes], context: _ContextLike) -> Any:
        """
        Encode a MAC address.

        :param Union[str, bytes] obj: The MAC address to encode.
        :param _ContextLike context: The context for encoding.
        :return: The encoded value.
        """
        if isinstance(obj, str):
            obj = obj.encode(self.struct.encoding or "utf-8")

        # replace unnecessary characters
        mac = re.sub(MACAddress.DELIMITERS, b"", obj)
        return binascii.unhexlify(mac)

    def decode(self, parsed: bytes, context: _ContextLike) -> bytes:
        """
        Decode an encoded MAC address.

        :param bytes parsed: The parsed bytes representing the MAC address.
        :param _ContextLike context: The context for decoding.
        :return: The decoded MAC address.
        """
        return binascii.b2a_hex(parsed, self.sep)


# shortcut for default MAC address format
MAC = MACAddress()
