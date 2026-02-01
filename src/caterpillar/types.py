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
from datetime import datetime
import ipaddress
import uuid

from .fields.common import (
    boolean,
    char,
    uint8,
    uint16,
    uint24,
    uint32,
    uint64,
    int8,
    int16,
    int24,
    int32,
    int64,
    float16,
    float32,
    float64,
    double,
    psize,
    pssize,
    Uuid,
    Pass,
    CString,
    Timestamp,
    void_ptr,
)
from .fields.varint import vint
from .fields.net import MAC, IPv4Address, IPv6Address
from .shortcuts import f

bool1_t = f[bool, 1]
"""1-bit integer field (boolean).

Represents a single bit typically used in bitfield definitions.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int1_t = f[int, 1]
"""1-bit integer field.

Represents a single signed bit typically used in bitfield definitions.

Usage Example:
  >>> @bitfield
  ... class Flags:
  ...     enabled: int1_t

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int2_t = f[int, 2]
"""2-bit integer field for compact bitfield storage.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int3_t = f[int, 3]
"""3-bit integer field for compact bitfield storage.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int4_t = f[int, 4]
"""4-bit integer field for compact bitfield storage.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int5_t = f[int, 5]
"""5-bit integer field for compact bitfield storage.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int6_t = f[int, 6]
"""6-bit integer field for compact bitfield storage.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int7_t = f[int, 7]
"""7-bit integer field for compact bitfield storage.

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""

int8_t = f[int, int8]
"""Signed 8-bit integer field.

Usage Example:
  >>> @bitfield
  ... class Packet:
  ...     value: int8_t

.. versionadded:: 2.8.0
"""

uint8_t = f[int, uint8]
"""Unsigned 8-bit integer field.

.. versionadded:: 2.8.0
"""

int16_t = f[int, int16]
"""Signed 16-bit integer field.

.. versionadded:: 2.8.0
"""

uint16_t = f[int, uint16]
"""Unsigned 16-bit integer field.

.. versionadded:: 2.8.0
"""

int32_t = f[int, int32]
"""Signed 32-bit integer field.

.. versionadded:: 2.8.0
"""

uint32_t = f[int, uint32]
"""Unsigned 32-bit integer field.

.. versionadded:: 2.8.0
"""

int64_t = f[int, int64]
"""Signed 64-bit integer field.

.. versionadded:: 2.8.0
"""

uint64_t = f[int, uint64]
"""Unsigned 64-bit integer field.

.. versionadded:: 2.8.0
"""

ssize_t = f[int, pssize]
"""Signed platform-sized integer field.

.. versionadded:: 2.8.0
"""

size_t = f[int, psize]
"""Unsigned platform-sized integer field.

.. versionadded:: 2.8.0
"""

float16_t = f[float, float16]
"""16-bit floating point field.

.. versionadded:: 2.8.0
"""

float32_t = f[float, float32]
"""32-bit floating point field.

.. versionadded:: 2.8.0
"""

float64_t = f[float, float64]
"""64-bit floating point field.

.. versionadded:: 2.8.0
"""

double_t = f[float, double]
"""Alias for 64-bit floating point field.

.. versionadded:: 2.8.0
"""

void_ptr_t = f[int, void_ptr]
"""Pointer-sized integer field representing a memory address.

.. versionadded:: 2.8.0
"""

cstr_t = f[str, CString(...)]
"""C-style null-terminated string field with a dynamic size.

Usage Example:
  >>> name: cstr_t

.. versionadded:: 2.8.0
"""

char_t = f[str, char]
"""Single character field.

.. versionadded:: 2.8.0
"""

boolean_t = f[bool, boolean]
"""Boolean field stored as a single byte.

.. versionadded:: 2.8.0
"""

pass_t = f[None, Pass]
"""Placeholder field that consumes no data and performs no action.

.. versionadded:: 2.8.0
"""

uint24_t = f[int, uint24]
"""Unsigned 24-bit integer field.

.. versionadded:: 2.8.0
"""

int24_t = f[int, int24]
"""Signed 24-bit integer field.

.. versionadded:: 2.8.0
"""

uuid_t = f[uuid.UUID, Uuid]
"""UUID field mapped to :class:`uuid.UUID`.

Usage Example:
  >>> identifier: uuid_t

.. versionadded:: 2.8.0
"""

vint_t = f[int, vint]
"""Variable-length integer field using a compact encoding.

.. versionadded:: 2.8.0
"""

MAC_t = f[bytes, MAC]
"""MAC address field represented as 6 raw bytes.

.. versionadded:: 2.8.0
"""

ipv6_t = f[ipaddress.IPv4Address, IPv6Address]
"""IPv6 address field mapped to :class:`ipaddress.IPv6Address`.

.. versionadded:: 2.8.0
"""

ipv4_t = f[ipaddress.IPv4Address, IPv4Address]
"""IPv4 address field mapped to :class:`ipaddress.IPv4Address`.

.. versionadded:: 2.8.0
"""

timestamp_t = f[datetime, Timestamp()]
"""Timestamp field mapped to :class:`datetime.datetime`.

.. versionadded:: 2.8.0
"""

balign_t = f[None, 0]
"""Bit-alignment field used to align to the next byte boundary in bitfields.

This type **MUST** be used together with :func:`Invisible` to remove it
from the constructor::

    @bitfield
    class Format:
        value: int2_t
        _    : balign_t     = Invisible() # not visible to the type checker

.. note::
    Only usable in bitfields.

.. versionadded:: 2.8.0
"""


__all__ = [
    "uint8_t",
    "uint16_t",
    "uint24_t",
    "uint32_t",
    "uint64_t",
    "int8_t",
    "int16_t",
    "int24_t",
    "int32_t",
    "int64_t",
    "float16_t",
    "float32_t",
    "float64_t",
    "double_t",
    "size_t",
    "ssize_t",
    "uuid_t",
    "pass_t",
    "cstr_t",
    "MAC_t",
    "ipv4_t",
    "ipv6_t",
    "vint_t",
    "int1_t",
    "int2_t",
    "int3_t",
    "int4_t",
    "int5_t",
    "int6_t",
    "int7_t",
    "void_ptr_t",
    "balign_t",
    "timestamp_t",
]
