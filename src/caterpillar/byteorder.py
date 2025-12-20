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
import inspect

from sys import maxsize
from platform import machine
from dataclasses import dataclass
from enum import Enum
from typing_extensions import override

from caterpillar.shared import ATTR_BYTEORDER
from caterpillar.context import CTX_ORDER


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
        setattr(other, ATTR_BYTEORDER, self)

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


class DynByteOrder:
    """Represents a dynamic byte order resolved at runtime.

    A dynamic byte order defers endian resolution until pack or unpack
    execution. Resolution may depend on the active context, a field
    value, or a user-provided callable.

    Supported concepts:

    - Root context resolution using CTX_ORDER
    - Context key lookup using a string or callable
    - Runtime resolution using a function
    - Per-field byte order overrides using addition syntax

    Using the root context byte order::

        @struct(order=Dynamic)
        class Format:
            a: uint16
            b: uint32

        pack(obj, **{CTX_ORDER: BigEndian})

    Using a context key::

        @struct(order=Dynamic(this.spec))
        class Format:
            spec: uint8
            a: uint16


    Using a function::

        def func():
            return BigEndian

        @struct(order=DynByteOrder(func=func))
        class Format:
            a: uint16

    Using a per-field dynamic byte order::

        a: Dynamic(this.spec) + uint16

    :param name: Human readable name for the byte order, defaults to None
    :type name: str, optional
    :param key: Context key or callable used to resolve byte order,
        defaults to None
    :type key: str or callable, optional
    :param func: Callable returning an object with a ch attribute,
        defaults to None
    :type func: callable, optional
    :param init_ch: Initial format character, defaults to None
    :type init_ch: str, optional
    """

    def __init__(
        self,
        name=None,
        key=None,
        func=None,
        init_ch=None,
    ) -> None:
        self.name = name or "<Dynamic>"
        self.__ch = init_ch or LITTLE_ENDIAN_FMT
        self.func = func
        self._ctx_func = False
        if func is not None:
            spec = inspect.getfullargspec(func)
            if len(spec.args) == 1:
                self._ctx_func = True
        self.key = key
        self.__key_str = isinstance(self.key, str)

    def __call__(self, key):
        """Create a derived dynamic byte order bound to a new key.

        :param key: Context key or callable used for byte order lookup
        :type key: str or callable
        :return: A new dynamic byte order instance
        :rtype: DynByteOrder
        """
        return DynByteOrder(self.name, key, self.func, self.__ch)

    def getch(self, context) -> str:
        """Resolve the byte order format character from a context.

        Resolution order:

        1. Function result, with or without context
        2. Context key lookup
        3. Root context CTX_ORDER value
        4. Boolean or string fallback

        Resolution prioritizes a callable, then a context key, and finally
        a root context fallback with default behavior.
        :param context: Context providing byte order information
        :type context: object
        :return: Struct format character representing byte order
        :rtype: str
        """
        if self.func is not None:
            if self._ctx_func:
                return self.func(context).ch
            else:
                return self.func().ch

        if self.key is not None:
            if self.__key_str:
                byte_order = context.__context_getattr__(self.key)
            else:
                byte_order = self.key(context)
        else:
            root_context = context._root
            byte_order = (root_context or {}).get(CTX_ORDER, SysNative)

        ch = getattr(byte_order, "ch", byte_order)
        if not isinstance(ch, str):
            ch = LITTLE_ENDIAN_FMT if bool(byte_order) else BigEndian.ch

        return ch

    @property
    def ch(self) -> str:
        """Return the active byte order character.

        The value may change dynamically by inspecting the caller frame
        and extracting a local variable named context.

        :return: Struct format character for byte order
        :rtype: str
        """
        frame = inspect.currentframe()
        if frame is not None and frame.f_back is not None:
            ctx_frame = frame.f_back
            context = ctx_frame.f_locals.get("context")
            if context is not None:
                self.__ch = self.getch(context)
        return self.__ch

    @ch.setter
    def ch(self, value: str) -> None:
        """Set the byte order format character explicitly.

        :param value: Struct format character to assign
        :type value: str
        :return: None
        :rtype: None
        """
        self.__ch = value

    def __add__(self, other):
        """Apply this byte order to another object.

        Delegates to the other object's byte order assignment method.

        :param other: Object supporting byte order assignment
        :type other: object
        :return: Result of the byte order assignment
        :rtype: object
        """
        return other.__set_byteorder__(self)

    @override
    def __repr__(self) -> str:
        return f"<DynByteOrder little={self.ch == LITTLE_ENDIAN_FMT}>"


LITTLE_ENDIAN_FMT = "<"

# Instances representing commonly used byte orders
Native = ByteOrder("Native", "=")
BigEndian = ByteOrder("Big Endian", ">")
LittleEndian = ByteOrder("Little Endian", LITTLE_ENDIAN_FMT)
NetEndian = ByteOrder("Network", "!")
SysNative = ByteOrder(
    "SysNative", "@", ByteOrder.Alignment.NATIVE, ByteOrder.Size.NATIVE
)
Dynamic = DynByteOrder()


def byteorder(obj, default=None):
    """
    Get the byte order of an object, defaulting to SysNative if not explicitly set.

    :param obj: The object to retrieve the byte order from.
    :return: The byte order of the object.
    """
    return getattr(obj, ATTR_BYTEORDER, default or SysNative)


def byteorder_is_little(obj) -> bool:
    """
    Check if the byte order of an object is little-endian.
    """
    return getattr(obj, "ch", LITTLE_ENDIAN_FMT) == LITTLE_ENDIAN_FMT


@dataclass(frozen=True)
class Arch:
    """
    Represents a system architecture with a name and an indication of whether it is 64-bit.

    :param name: The name of the architecture.
    :param ptr_size: the amount of bits one pointer takes
    """

    name: str
    ptr_size: int


system_arch: Arch = Arch(machine(), 64 if maxsize > 2**32 else 32)

# common architectures
x86 = Arch("x86", 32)
x86_64 = Arch("x86-64", 64)
ARM = Arch("ARM", 32)
ARM64 = Arch("ARM64", 64)
AARCH64 = ARM64
PowerPC = Arch("PowerPC", 32)
PowerPC64 = Arch("PowerPC64", 64)
MIPS = Arch("MIPS", 32)
MIPS64 = Arch("MIPS64", 64)
SPARC = Arch("SPARC", 32)
SPARC64 = Arch("SPARC64", 64)
RISC_V64 = Arch("RISK-V64", 64)
RISC_V = Arch("RISK-V", 32)
AMD = Arch("AMD", 32)
AMD64 = Arch("AMD64", 64)
