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
from io import IOBase
from types import EllipsisType
from typing import (
    Any,
    Callable,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
    type_check_only,
)

_IT = TypeVar("_IT", default=Any)
_IT_co = TypeVar("_IT_co", covariant=True, default=Any)
_IT_contra = TypeVar("_IT_contra", contravariant=True, default=Any)
_OT = TypeVar("_OT", default=Any)
_OT_co = TypeVar("_OT_co", covariant=True, default=Any)

_StreamType = IOBase
_StreamFactory = Callable[[], _StreamType]

_GreedyType = EllipsisType
_PrefixedType = slice  # [_StructLike[int, int], NoneType, NoneType]

_LengthT = Union[int, _PrefixedType, _GreedyType, _ContextLambda]

@runtime_checkable
class _ContextLike(Protocol):
    def __init__(self, **kwargs) -> None: ...
    @property
    def _root(self) -> Optional[_ContextLike]: ...
    def __context_getattr__(self, path: str) -> Any: ...
    def __context_setattr__(self, path: str, value: Any) -> None: ...
    def __getitem__(self, key, /) -> Any: ...
    def __setitem__(self, key, value: Any, /) -> None: ...
    def get(self, key: str, default: Any | None = None, /) -> Any: ...

_ContextLambdaReturnT_co = TypeVar(
    "_ContextLambdaReturnT_co", covariant=True, default=Any
)

@runtime_checkable
class _ContextLambda(Protocol[_ContextLambdaReturnT_co]):
    def __call__(self, context: _ContextLike) -> _ContextLambdaReturnT_co: ...

@runtime_checkable
class _StructLike(Protocol[_IT_contra, _OT_co]):
    def __size__(self, context: _ContextLike) -> int: ...
    def __unpack__(self, context: _ContextLike) -> _OT_co: ...
    def __pack__(self, obj: _IT_contra, context: _ContextLike) -> None: ...
    def __type__(self) -> Optional[Union[type, str]]: ...

_StructT = Union[_ContainsStruct[_IT, _OT], _StructLike[_IT, _OT], _ContextLambda]

@runtime_checkable
class _ContainsStruct(Protocol[_IT_contra, _OT]):
    __struct__: _StructLike[_IT_contra, _OT]

@runtime_checkable
class _SupportsActionUnpack(Protocol):
    def __action_pack__(self, context: _ContextLike) -> None:
        pass

@runtime_checkable
class _SupportsActionPack(Protocol):
    def __action_unpack__(self, context: _ContextLike) -> None:
        pass

_ActionLike = Union[_SupportsActionPack, _SupportsActionUnpack]

@runtime_checkable
class _SupportsPack(Protocol[_IT_contra]):
    def __pack__(self, obj: _IT_contra, context: _ContextLike) -> None: ...

@runtime_checkable
class _SupportsSize(Protocol):
    def __size__(self, context: _ContextLike) -> int: ...

@runtime_checkable
class _SupportsType(Protocol):
    def __type__(self) -> type | str | None: ...

@runtime_checkable
class _SupportsUnpack(Protocol[_OT_co]):
    def __unpack__(self, context: _ContextLike) -> _OT_co: ...

_SwitchLambda = Callable[[Any, _ContextLike], _StructLike[_IT, _OT]]
_SwitchLike = Union[
    dict[Any, Union[_ContainsStruct[_IT, _OT], _StructLike[_IT, _OT]]],
    _SwitchLambda[_IT, _OT],
]

@runtime_checkable
class _SupportsBits(Protocol):
    def __bits__(self) -> int: ...

@runtime_checkable
class _ContainsBits(Protocol):
    __bits__: int

@type_check_only
class _ArchLike(Protocol):
    name: str
    ptr_size: int

    def __init__(self, name: str, ptr_size: int) -> None: ...

@type_check_only
class _SupportsSetEndian(Protocol[_OT_co]):
    def __set_byteorder__(self, order: _EndianLike) -> _OT_co: ...

@type_check_only
class _EndianLike(Protocol):
    name: str
    ch: str

    def __add__(self, other: _SupportsSetEndian[_OT]) -> _OT: ...

@type_check_only
class _OptionLike(Protocol):
    name: str
    value: Any

__all__ = [
    "_ContextLike",
    "_ContextLambda",
    "_SupportsActionUnpack",
    "_SupportsActionPack",
    "_SupportsPack",
    "_SupportsUnpack",
    "_SupportsSize",
    "_StructLike",
    "_SupportsType",
    "_ContainsStruct",
    "_SwitchLike",
    "_SupportsBits",
    "_ContainsBits",
]
