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
from ._mixin import FieldStruct
from caterpillar.abc import _ContextLambda, _ContextLike, _StructLike
from caterpillar.options import Flag
from typing import Dict, Generic, Optional, Type, TypeVar

PTR_STRICT: Flag[None]

_PtrValueT = TypeVar("_PtrValueT")

class pointer(Generic[_PtrValueT], int):
    obj: Optional[_PtrValueT]
    def get(self) -> _PtrValueT | None: ...

class Pointer(FieldStruct[int, pointer[_PtrValueT]]):
    model: _StructLike[_PtrValueT, _PtrValueT] | None
    struct: _StructLike[int, int] | _ContextLambda[_StructLike[int, int]]
    def __init__(
        self,
        struct: _StructLike[int, int] | _ContextLambda[_StructLike[int, int]],
        model: _StructLike[_PtrValueT, _PtrValueT] | None = None,
    ) -> None: ...
    def __mul__(
        self, model: _StructLike[_PtrValueT, _PtrValueT]
    ) -> Pointer[_PtrValueT]: ...
    def __type__(self) -> Type[pointer[_PtrValueT]]: ...
    def __size__(self, context: _ContextLike) -> int: ...
    def unpack_single(self, context: _ContextLike) -> pointer[_PtrValueT]: ...
    def pack_single(self, obj: int, context: _ContextLike) -> None: ...

UNSIGNED_POINTER_TYS: Dict
SIGNED_POINTER_TYS: Dict

def uintptr_fn(context: _ContextLike) -> _StructLike[int, int]: ...
def intptr_fn(context: _ContextLike) -> _StructLike[int, int]: ...

uintptr: Pointer[None]
intptr: Pointer[None]

class relative_pointer(pointer[_PtrValueT]):
    base: int
    @property
    def absolute(self) -> int: ...

class RelativePointer(Pointer[_PtrValueT]):
    def __type__(self) -> relative_pointer[_PtrValueT]: ...

offintptr: RelativePointer[None]
offuintptr: RelativePointer[None]
