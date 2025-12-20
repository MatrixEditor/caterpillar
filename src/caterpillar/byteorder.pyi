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
from enum import Enum
from typing import Callable
from typing_extensions import Final

from caterpillar.abc import (
    _EndianLike,
    _ArchLike,
    _SupportsSetEndian,
    _OT,
    _ContextLambda,
    _ContextLike,
)

class ByteOrder(_EndianLike):
    name: str
    ch: str

    class Alignment(Enum):
        NONE = 0
        NATIVE = 1

    alignment: Alignment

    class Size(Enum):
        STANDARD = 0
        NATIVE = 1

    size: Size

    def apply(self, other: ByteOrder) -> None: ...
    def __add__(self, other: _SupportsSetEndian[_OT]) -> _OT: ...
    def __or__(self, other: ByteOrder): ...
    def __init__(
        self,
        name: str,
        ch: str,
        alignment: Alignment | None = ...,
        size: Size | None = ...,
    ) -> None: ...

class DynByteOrder:
    name: str
    ch: str
    key: str | _ContextLambda[str | _EndianLike | bool] | None
    func: Callable[[], _EndianLike] | _ContextLambda[_EndianLike] | None

    def __init__(
        self,
        name: str | None = None,
        key: str | _ContextLambda[str | _EndianLike | bool] | None = None,
        func: Callable[[], _EndianLike] | _ContextLambda[_EndianLike] | None = None,
        init_ch: str | None = None,
    ) -> None: ...
    def __call__(
        self, key: str | _ContextLambda[str | _EndianLike | bool]
    ) -> DynByteOrder: ...
    def __add__(self, other: _SupportsSetEndian[_OT]) -> _OT: ...
    def getch(self, context: _ContextLike) -> str: ...

LITTLE_ENDIAN_FMT: str
Native: Final[ByteOrder]
BigEndian: Final[ByteOrder]
LittleEndian: Final[ByteOrder]
NetEndian: Final[ByteOrder]
SysNative: Final[ByteOrder]
Dynamic: Final[DynByteOrder]

def byteorder(obj, default: _EndianLike | None = None) -> _EndianLike: ...
def byteorder_is_little(endian: _EndianLike) -> bool: ...

class Arch(_ArchLike):
    name: str
    ptr_size: int

    def __init__(self, name: str, ptr_size: int) -> None: ...

system_arch: Final[Arch]
x86: Final[Arch]
x86_64: Final[Arch]
ARM: Final[Arch]
ARM64: Final[Arch]
AARCH64: Final[Arch]
PowerPC: Final[Arch]
PowerPC64: Final[Arch]
MIPS: Final[Arch]
MIPS64: Final[Arch]
SPARC: Final[Arch]
SPARC64: Final[Arch]
RISC_V64: Final[Arch]
RISC_V: Final[Arch]
AMD: Final[Arch]
AMD64: Final[Arch]
