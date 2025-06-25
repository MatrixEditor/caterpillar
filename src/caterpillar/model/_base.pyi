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
from typing import Any, Dict, Generic, Iterable, Self, Optional, Type, TypeVar, Union

from caterpillar.abc import _StructLike, _ActionLike, _ContextLike, _ContainsStruct
from caterpillar.byteorder import ByteOrder, Arch
from caterpillar.fields._base import Field
from caterpillar.fields._mixin import FieldMixin
from caterpillar.options import Flag

_SeqModelT = TypeVar(
    "_SeqModelT", default=Dict[str, Union[_StructLike, _ContainsStruct, type]]
)

class Sequence(FieldMixin, Generic[_SeqModelT], _StructLike[_SeqModelT, _SeqModelT]):
    model: Any
    fields: list[Field | tuple[_ActionLike, None]]
    order: Optional[ByteOrder]
    arch: Optional[Arch]
    options: set[Flag]
    field_options: set[Flag]
    is_union: bool
    def __init__(
        self,
        model: Optional[dict[str, Field]] = None,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        options: Optional[Iterable[Flag]] = None,
        field_options: Optional[Iterable[Flag]] = None,
    ) -> None: ...
    def __add__(self, sequence) -> Self: ...
    def __sub__(self, sequence) -> Self: ...
    __iadd__ = __add__
    __isub__ = __sub__
    def has_option(self, option: Flag) -> bool: ...
    def add_field(self, name: str, field: Field, included: bool = False) -> None: ...
    def add_action(self, action: _ActionLike) -> None: ...
    def del_field(self, name: str, field: Field) -> None: ...
    def get_members(self) -> dict[str, Field]: ...
    def unpack_one(self, context: _ContextLike) -> _SeqModelT: ...
    def get_value(self, obj: Any, name: str, field: Field) -> Any: ...
    def pack_one(self, obj: _SeqModelT, context: _ContextLike) -> None: ...
    def __size__(self, context: _ContextLike) -> int: ...
    def __unpack__(self, context: _ContextLike) -> _SeqModelT: ...
    def __type__(self) -> Type[_SeqModelT]: ...
    def __pack__(self, obj: _SeqModelT, context: _ContextLike) -> None: ...
