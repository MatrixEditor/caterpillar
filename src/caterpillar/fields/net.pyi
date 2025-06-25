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
from re import Pattern
from ipaddress import IPv4Address, IPv6Address

from ._base import singleton as singleton
from .common import (
    Bytes as Bytes,
    Transformer as Transformer,
    UInt as UInt,
    uint32 as uint32,
)
from caterpillar.abc import _ContextLike

IPv4Address = Transformer[IPv4Address, int, IPv4Address, int]
IPv6Address = Transformer[IPv6Address, int, IPv6Address, int]

class MACAddress(Transformer[str | bytes, bytes, bytes, bytes]):
    DELIMITERS: Pattern
    sep: str
    def __init__(self, sep: str | None = None) -> None: ...
    def encode(self, obj: str | bytes, context: _ContextLike) -> bytes: ...
    def decode(self, parsed: bytes, context: _ContextLike) -> bytes: ...

MAC: MACAddress
