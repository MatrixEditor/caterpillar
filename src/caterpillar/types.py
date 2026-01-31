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
    size,
    ssize,
    Uuid,
    Pass,
    CString,
    Timestamp,
    void_ptr,
)
from .fields.varint import vint
from .fields.net import MAC, IPv4Address, IPv6Address
from .shortcuts import f

int1_t = f[int, 1]
int2_t = f[int, 2]
int3_t = f[int, 3]
int4_t = f[int, 4]
int5_t = f[int, 5]
int6_t = f[int, 6]
int7_t = f[int, 7]
int8_t = f[int, int8]
uint8_t = f[int, uint8]
int16_t = f[int, int16]
uint16_t = f[int, uint16]
int32_t = f[int, int32]
uint32_t = f[int, uint32]
int64_t = f[int, int64]
uint64_t = f[int, uint64]
ssize_t = f[int, ssize]
size_t = f[int, size]
float16_t = f[float, float16]
float32_t = f[float, float32]
float64_t = f[float, float64]
double_t = f[float, double]
void_ptr_t = f[int, void_ptr]
cstr_t = f[str, CString(...)]
char_t = f[str, char]
boolean_t = f[bool, boolean]
pass_t = f[None, Pass]
uint24_t = f[int, uint24]
int24_t = f[int, int24]
uuid_t = f[uuid.UUID, Uuid]
vint_t = f[int, vint]
MAC_t = f[bytes, MAC]
ipv6_t = f[ipaddress.IPv4Address, IPv6Address]
ipv4_t = f[ipaddress.IPv4Address, IPv4Address]
timestamp_t = f[datetime, Timestamp()]

# TODO(REVISIT): naming convention
# special type
balign_t = f[None, 0]

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
