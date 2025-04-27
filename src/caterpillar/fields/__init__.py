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
from ._base import Field, INVALID_DEFAULT, DEFAULT_OPTION, singleton
from ._mixin import FieldMixin, FieldStruct, Chain, Operator
from .common import (
    PyStructFormattedField,
    Transformer,
    Const,
    ConstBytes,
    ConstString,
    Enum,
    String,
    Bytes,
    Memory,
    Computed,
    Pass,
    CString,
    Prefixed,
    Int,
    UInt,
    padding,
    char,
    boolean,
    int8,
    uint8,
    int16,
    uint16,
    int24,
    uint24,
    int32,
    uint32,
    int64,
    uint64,
    ssize_t,
    size_t,
    float16,
    float32,
    float64,
    double,
    void_ptr,
    Uuid,
    Aligned,
    align,
    Lazy,
)
from .varint import VarInt, VARINT_LSB, vint
from .compression import (
    Compressed,
    ZLibCompressed,
    Bz2Compressed,
    LZMACompressed,
    LZOCompressed,
)
from .crypto import Encrypted, Xor, Or, And
from .net import IPv4Address, IPv6Address, MAC, MACAddress
from .pointer import uintptr, intptr, offintptr, offuintptr, Pointer
from .conditional import ConditionalChain, If, Else, ElseIf
from .hook import IOHook
from .digest import (
    Digest,
    Algorithm,
    Md5,
    Sha1,
    Sha2_256,
    Sha2_224,
    Sha2_384,
    Sha2_512,
    Sha3_224,
    Sha3_256,
    Sha3_384,
    Sha3_512,
    Crc32,
    Adler,
    HMAC,
)
