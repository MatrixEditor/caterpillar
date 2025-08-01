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
from typing import (
    Any,
    Generic,
    Iterable,
    Self,
    Optional,
    Type,
    TypeVar,
    Union,
    override,
)

from caterpillar.abc import (
    _StructLike,
    _ActionLike,
    _ContextLike,
    _ContainsStruct,
    _OptionLike,
    _ContextLambda,
    _EndianLike,
    _ArchLike,
)
from caterpillar.byteorder import ByteOrder, Arch
from caterpillar.fields._base import Field
from caterpillar.fields._mixin import FieldMixin

_SeqModelT = TypeVar("_SeqModelT", default=dict[str, Any])

class _Member:
    name: str | None
    field: Field[Any, Any] | _ActionLike
    include: bool
    is_action: bool
    action_unpack: _ContextLambda[None]
    action_pack: _ContextLambda[None]

    def __init__(
        self,
        name: str | None,
        field: Field[Any, Any] | _ActionLike,
        include: bool = ...,
        is_action: bool = ...,
    ) -> None: ...
    @override
    def __eq__(self, value: object, /) -> bool: ...

class Sequence(FieldMixin[_SeqModelT, _SeqModelT]):
    model: dict[str, Any]
    fields: list[_Member]
    order: _EndianLike
    arch: _ArchLike
    options: set[_OptionLike]
    field_options: set[_OptionLike]
    is_union: bool
    _member_map_: dict[str, Field]
    def __init__(
        self,
        model: dict[str, Any],
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> None: ...
    def __add__(self, sequence) -> Self: ...
    def __sub__(self, sequence) -> Self: ...
    __iadd__ = __add__
    __isub__ = __sub__
    def has_option(self, option: _OptionLike) -> bool: ...
    def add_field(self, name: str, field: Field, included: bool = False) -> None: ...
    def add_action(self, action: _ActionLike) -> None: ...
    def del_field(self, name: str, field: Field) -> None: ...
    def get_members(self) -> dict[str, Field]: ...
    def unpack_one(self, context: _ContextLike) -> _SeqModelT: ...
    def get_value(self, obj: Any, name: str, field: Field) -> Any: ...
    def pack_one(self, obj: _SeqModelT, context: _ContextLike) -> None: ...
    def __size__(self, context: _ContextLike) -> int: ...
    def __unpack__(self, context: _ContextLike) -> _SeqModelT: ...
    def __type__(self) -> type[_SeqModelT]: ...
    def __pack__(self, obj: _SeqModelT, context: _ContextLike) -> None: ...
    def _set_default(self, name: str, value: Any) -> Any: ...
    def _included(self, name: str, default: Any | None, annotation: Any) -> bool: ...
    def _process_default(
        self,
        name: str,
        annotation: Any,
        had_default: bool = ...,
    ) -> Any: ...
    def _replace_type(self, name: str, type_: type) -> None: ...
    def _remove_from_model(self, name: str) -> None: ...
    def _process_model(self) -> None: ...
    def _prepare_fields(self) -> dict[str, Any]: ...
    def _process_annotation(
        self,
        annotation: Any,
        default: Any,
        order: ByteOrder,
        arch: Arch,
    ) -> _StructLike: ...
    def _process_field(self, name: str, annotation: Any, default: Any) -> Field: ...
