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
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    overload,
)

from caterpillar.abc import _ContextLike, _ActionLike
from caterpillar.byteorder import Arch, ByteOrder
from caterpillar.options import B_GROUP_END, B_GROUP_NEW, Flag
from caterpillar.fields._base import Field
from caterpillar.model._struct import Struct

_ModelT = TypeVar("_ModelT")

DEFAULT_ALIGNMENT: int

def getbits(obj: Any) -> int: ...
def issigned(obj: Any) -> bool: ...

class SetAlignment:
    alignment: int
    def __init__(self, new_alignment: int) -> None: ...
    @staticmethod
    def flag(new_alignment: int) -> Flag[int]: ...
    def __hash__(self) -> int: ...

NewGroup = B_GROUP_NEW
EndGroup = B_GROUP_END

_VT = TypeVar("_VT", default=int)

class BitfieldValueFactory(Generic[_VT]):
    def to_int(self, obj: _VT) -> int: ...
    def from_int(self, value: int) -> _VT: ...

_EnumT = TypeVar("_EnumT", bound=Enum)

class EnumFactory(Generic[_EnumT], BitfieldValueFactory[_EnumT | int]):
    strict: bool
    def __init__(self, model: Type[_EnumT], strict: bool = ...) -> None: ...
    def from_int(self, value: int) -> _EnumT | int: ...

class CharFactory(BitfieldValueFactory[str]):
    def from_int(self, value: int) -> str: ...
    def to_int(self, obj: str) -> int: ...

class BitfieldEntry:
    bit: int
    width: int
    name: str
    factory: Optional[BitfieldValueFactory]
    action: Optional[_ActionLike]
    low_mask: int

    def __init__(
        self,
        bit: int,
        width: int,
        name: str,
        factory: BitfieldValueFactory | Type | None = ...,
        action: _ActionLike | None = ...,
    ) -> None: ...
    @staticmethod
    def new_action(action: _ActionLike) -> BitfieldEntry: ...
    def shift(self, value_width: int) -> int: ...
    def is_action(self) -> bool: ...

class BitfieldGroup:
    bit_count: int
    entries: List[BitfieldEntry | Field]
    def __init__(self, bit_count: int) -> None: ...
    def is_field(self) -> bool: ...
    def get_field(self) -> Field: ...
    def set_field(self, field: Field) -> None: ...
    def align_to(self, alignment: int) -> None: ...
    def is_empty(self) -> bool: ...
    def get_size(self, context: _ContextLike | None = ...) -> int: ...
    def get_bits(self, context: _ContextLike | None = ...) -> int: ...

class Bitfield(Struct[_ModelT]):
    alignment: int
    groups: List[BitfieldGroup]
    def __init__(
        self,
        model,
        order: ByteOrder | None = ...,
        arch: Arch | None = ...,
        options: Iterable[Flag] | None = ...,
        field_options: Iterable[Flag] | None = ...,
        alignment: int | None = ...,
    ) -> None: ...
    def __add__(self, sequence): ...
    def __size__(self, context: _ContextLike) -> int: ...
    def __bits__(self) -> int: ...
    def unpack_one(self, context: _ContextLike): ...
    def pack_one(self, obj: _ModelT, context: _ContextLike) -> None: ...
    def add_action(self, action: _ActionLike) -> None: ...
    def get_entry(self, name: str) -> Optional[BitfieldEntry]: ...
    def _process_align(
        self, options: Optional[Iterable[Flag | SetAlignment]]
    ) -> Field: ...
    def _process_bits(
        self,
        name: str,
        bits: int,
        factory: Optional[BitfieldValueFactory | Type] = ...,
        options: Optional[Iterable[Flag | SetAlignment]] = ...,
    ) -> Field: ...
    def _process_bits_field(
        self,
        name: str,
        field: Field,
        factory: Optional[BitfieldValueFactory | Type] = ...,
        options: Optional[Iterable[Flag | SetAlignment]] = ...,
    ) -> Field: ...
    def _process_options(
        self,
        options: Iterable[Flag | SetAlignment],
        entry: Optional[BitfieldEntry] = ...,
    ) -> bool: ...
    def _new_group(self, alignment: int) -> BitfieldGroup: ...
    def _process_alignment_option(self, option: Flag | SetAlignment) -> bool: ...

@overload
def bitfield(
    cls: None = None,
    /,
    *,
    options: Iterable[Flag] | None = ...,
    order: ByteOrder | None = ...,
    arch: Arch | None = ...,
    field_options: Iterable[Flag] | None = ...,
) -> Callable[[Type[_ModelT]], Type[_ModelT]]: ...
@overload
def bitfield(
    cls: Type[_ModelT],
    /,
    *,
    options: Iterable[Flag] | None = ...,
    order: ByteOrder | None = ...,
    arch: Arch | None = ...,
    field_options: Iterable[Flag] | None = ...,
) -> Type[_ModelT]: ...
