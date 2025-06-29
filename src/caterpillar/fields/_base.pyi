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
from caterpillar import registry
from caterpillar.abc import (
    _ContextLambda,
    _ContextLike,
    _GreedyType,
    _PrefixedType,
    _StructLike,
    _SwitchLike,
    _IT,
    _OT,
    _LengthT,
    _StructT,
)
from caterpillar.byteorder import (
    Arch,
    ByteOrder,
)
from caterpillar.options import (
    Flag,
)
from typing import Any, Optional, Self, Type, TypeVar

_T = TypeVar("_T")

def singleton(cls: Type[_T]) -> _T: ...

INVALID_DEFAULT: object = ...
DEFAULT_OPTION: object = ...

class Field(_StructLike[_IT, _OT]):
    struct: _StructT[_IT, _OT]
    order: ByteOrder
    offset: _ContextLambda | int
    flags: dict[int, Flag]
    amount: _LengthT
    options: Optional[_SwitchLike[_IT, _OT]]
    condition: _ContextLambda | bool
    arch: Arch
    default: _OT | None
    bits: _ContextLambda | int | None
    def __init__(
        self,
        struct: _StructT[_IT, _OT],
        order: ByteOrder | None = None,
        offset: _ContextLambda | int = -1,
        flags: Optional[set[Flag]] = None,
        amount: _ContextLambda | int | _PrefixedType = 0,
        options: _SwitchLike | dict[Any, _StructLike] | None = None,
        condition: _ContextLambda | bool = True,
        arch: Optional[Arch] = None,
        default: _OT | None = ...,
        bits: _ContextLambda | int | None = None,
    ) -> None: ...
    def __or__(self, flag: Flag) -> Self: ...
    def __xor__(self, flag: Flag) -> Self: ...
    def __matmul__(self, offset: _ContextLambda | int) -> Self: ...
    def __getitem__(self, dim: _LengthT) -> Self: ...
    def __rshift__(self, switch: _SwitchLike[_IT, _OT]) -> Self: ...
    def __floordiv__(self, condition: _ContextLambda | bool) -> Self: ...
    def __rsub__(self, bits: _ContextLambda | int) -> Self: ...
    def __set_byteorder__(self, order: ByteOrder) -> Self: ...
    def __type__(self) -> type: ...
    def __unpack__(self, context: _ContextLike) -> _OT: ...
    def __pack__(self, obj: _IT, context: _ContextLike) -> None: ...
    def __size__(self, context: _ContextLike) -> int: ...
    __ixor__ = __xor__
    __ior__ = __or__
    __ifloordiv__ = __floordiv__
    __irshift__ = __rshift__
    __imatmul__ = __matmul__
    __isub__ = __rsub__
    def _verify_context_value(self, value: Any, expected: type) -> None: ...
    def is_seq(self) -> bool: ...
    def is_enabled(self, context: _ContextLike) -> bool: ...
    def has_condition(self) -> bool: ...
    def has_flag(self, flag: Flag) -> bool: ...
    def length(self, context: _ContextLike) -> int | _GreedyType | _PrefixedType: ...
    def get_struct(
        self, value: Any, context: _ContextLike
    ) -> _StructLike[_IT, _OT]: ...
    def get_offset(self, context: _ContextLike) -> int: ...
    def get_type(self) -> type: ...
    def get_name(self) -> str | None: ...

class _CallableTypeConverter(registry.TypeConverter):
    def matches(self, annotation: Any) -> bool: ...
    def convert(self, annotation: Any, kwargs: dict) -> Field: ...
