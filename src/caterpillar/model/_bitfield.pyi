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
from typing import Any, Callable, Dict, Iterable, Optional, Self, Type, TypeVar, overload

from caterpillar.abc import _ContextLike
from caterpillar.byteorder import Arch, ByteOrder
from caterpillar.options import Flag
from caterpillar.fields._base import Field
from caterpillar.model._struct import Struct

_ModelT = TypeVar("_ModelT")

BitTuple = tuple[int, int, type]
BITS_ATTR: str
SIGNED_ATTR: str

def getbits(obj: Any) -> int: ...
def issigned(obj: Any) -> bool: ...

class BitFieldGroup:
    size: int
    pos: int
    fmt: str
    fields: dict[BitTuple, Field] = ...
    def __init__(
        self,
        size: int,
        pos: int,
        fields: Optional[Dict[BitTuple, Field]] = None,
    ) -> None: ...

class BitField(Struct[_ModelT]):
    groups: list[BitFieldGroup]
    __bits__: int
    __fmt__: str

    def __init__(
        self,
        model: Type[_ModelT],
        options: Optional[Iterable[Flag]] = None,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        field_options: Optional[Flag] = None,
    ) -> None: ...
    def __add__(self, other: BitField) -> Self: ...
    def __size__(self, context: _ContextLike) -> int: ...
    def group(self, bit_index: int) -> BitFieldGroup | None: ...
    def unpack_one(self, context: _ContextLike) -> _ModelT: ...
    def pack_one(self, obj: _ModelT, context: _ContextLike) -> None: ...

@overload
def bitfield(
    cls: None = None,
    /,
    *,
    options: Iterable[Flag] | None = None,
    order: ByteOrder | None = None,
    arch: Arch | None = None,
    field_options: Iterable[Flag] | None = None,
) -> Callable[[Type[_ModelT]], Type[_ModelT]]: ...

@overload
def bitfield(
    cls: Type[_ModelT],
    /,
    *,
    options: Iterable[Flag] | None = None,
    order: ByteOrder | None = None,
    arch: Arch | None = None,
    field_options: Iterable[Flag] | None = None,
) -> Type[_ModelT]:...

