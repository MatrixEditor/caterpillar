# Copyright (C) MatrixEditor 2023
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
from __future__ import annotations

from sys import maxsize
from platform import machine

from dataclasses import dataclass
from enum import Enum

# constant to identify the byteorder of an object
BYTEORDER_FIELD = "__byteorder__"


@dataclass(frozen=True)
class ByteOrder:
    """
    Represents byte order information, including alignment and size.

    :param name: A string representing the name of the byte order.
    :param ch: A string representing the character used to specify the byte
               order in struct format strings.
    :param alignment: An enumeration representing the alignment (default
                      is `Alignment.NONE`).
    :param size: An enumeration representing the size (default is
                 `Size.STANDARD`).
    """

    name: str
    ch: str

    class Alignment(Enum):
        NONE = 0
        NATIVE = 1

    alignment: Alignment = Alignment.NONE

    class Size(Enum):
        STANDARD = 0
        NATIVE = 1

    size: Size = Size.STANDARD

    def apply(self, other):
        """
        Applies the byte order information to another object.

        :param other: The object to which the byte order information should be applied.
        """
        setattr(other, BYTEORDER_FIELD, self)

    def __add__(self, other):
        """
        Adds the byte order information to another object using the
        `__set_byteorder__` method.

        :param other: The object to which the byte order information should be added.
        :return: The modified object.
        """
        return other.__set_byteorder__(self)

    def __or__(self, other):
        """
        Applies the byte order information to another object using the `apply` method.

        :param other: The object to which the byte order information should be applied.
        :return: The modified object.
        """
        self.apply(other)
        return other


# Instances representing commonly used byte orders
Native = ByteOrder("Native", "=")
BigEndian = ByteOrder("Big Endian", ">")
LittleEndian = ByteOrder("Little Endian", "<")
NetEndian = ByteOrder("Network", "!")
SysNative = ByteOrder(
    "SysNative", "@", ByteOrder.Alignment.NATIVE, ByteOrder.Size.NATIVE
)


def byteorder(obj) -> ByteOrder:
    """
    Get the byte order of an object, defaulting to SysNative if not explicitly set.

    :param obj: The object to retrieve the byte order from.
    :return: The byte order of the object.
    """
    return getattr(obj, BYTEORDER_FIELD, SysNative)


@dataclass(frozen=True)
class Arch:
    """
    Represents a system architecture with a name and an indication of whether it is 64-bit.

    :param name: The name of the architecture.
    :param is_64: A boolean indicating whether the architecture is 64-bit.
    """

    name: str
    is_64: bool


def get_system_arch() -> Arch:
    """
    Get the system architecture.

    :return: An instance of Arch representing the system architecture.
    """
    return Arch(machine(), maxsize > 2**32)
