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
from abc import abstractmethod
from collections.abc import Iterable, Collection
from io import IOBase
from types import EllipsisType, NoneType
from typing import (
    Any,
    Callable,
    Protocol,
    TypeVar,
    runtime_checkable,
)
from typing_extensions import Final

_IT = TypeVar("_IT", default=Any)
_IT_co = TypeVar("_IT_co", covariant=True, default=Any)
_IT_contra = TypeVar("_IT_contra", contravariant=True, default=Any)
_OT = TypeVar("_OT", default=Any)
_OT_co = TypeVar("_OT_co", covariant=True, default=Any)
_ContextLambdaReturnT_co = TypeVar(
    "_ContextLambdaReturnT_co", covariant=True, default=Any
)

_StreamType = IOBase
_StreamFactory = Callable[[], _StreamType]

_GreedyType = EllipsisType


@runtime_checkable
class _ContextLike(Protocol):
    """
    A dictionary-like object used as a context for packing and unpacking.

    It allows direct attribute access and modification.
    """

    def __context_getattr__(self, path: str) -> Any: ...
    def __context_setattr__(self, path: str, value: Any) -> None: ...

    _root: "_ContextLike | None"

    def __getitem__(self, key: str, /) -> Any: ...  # pyright: ignore[reportAny]
    def __setitem__(self, key: str, value: Any, /) -> None: ...
    def get(self, key: str, default: Any | None = None, /) -> Any: ...


@runtime_checkable
class _ContextLambda(Protocol[_ContextLambdaReturnT_co]):
    """
    An abstract base class for a lambda function that takes a _ContextLike
    object as an argument.
    """

    def __call__(self, context: _ContextLike) -> _ContextLambdaReturnT_co: ...


@runtime_checkable
class _SupportsActionUnpack(Protocol):
    def __action_pack__(self, context: _ContextLike) -> None: ...


@runtime_checkable
class _SupportsActionPack(Protocol):
    def __action_unpack__(self, context: _ContextLike) -> None: ...


@runtime_checkable
class _SupportsPack(Protocol[_IT_co]):
    """
    An abstract base class for objects that support packing data into a binary stream.
    """

    def __pack__(self, obj: _IT, context: _ContextLike) -> None: ...


@runtime_checkable
class _SupportsUnpack(Protocol[_OT_co]):
    """
    An abstract base class for objects that support unpacking data from a binary stream.
    """

    def __unpack__(self, context: _ContextLike) -> _OT_co: ...


@runtime_checkable
class _SupportsSize(Protocol):
    """
    An abstract base class for objects that support determining the size of packed data.
    """

    def __size__(self, context: _ContextLike) -> int: ...


@runtime_checkable
class _StructLike(Protocol[_IT_contra, _OT_co]):
    """
    An abstract base class for struct-like objects that can be packed, unpacked, and have a size.
    """

    def __size__(self, context: _ContextLike) -> int: ...
    def __unpack__(self, context: _ContextLike) -> _OT_co: ...
    def __pack__(self, obj: _IT_contra, context: _ContextLike) -> None: ...
    def __type__(self) -> type | str | None: ...


_PrefixedType = slice # [_StructLike[int, int], NoneType, NoneType]
_LengthT = int | _PrefixedType | _GreedyType | _ContextLambda[int]


@runtime_checkable
class _SupportsType(Protocol):
    def __type__(self) -> type | str | None: ...


class _ContainsStruct(Protocol):
    """
    An abstract base class indicating that a class contains a _StructLike object.
    """

    __struct__: _StructLike


@runtime_checkable
class _SwitchLambda(Protocol):
    """
    An abstract base class for a switch-like object that generates a _StructLike
    based on a value and context.
    """

    @abstractmethod
    def __call__(self, value: Any, context: _ContextLike, **kwds) -> _StructLike: ...


@runtime_checkable
class _SupportsBits(Protocol):
    def __bits__(self) -> int: ...


@runtime_checkable
class _ContainsBits(Protocol):
    __bits__: int


class _ArchLike(Protocol):
    name: str
    ptr_size: int

    def __init__(self, name: str, ptr_size: int) -> None: ...


class _SupportsSetEndian(Protocol[_OT_co]):
    def __set_byteorder__(self, order: "_EndianLike") -> _OT_co: ...


class _EndianLike(Protocol):
    name: Final[str]

    @property
    def ch(self) -> str: ...
    def __add__(self, other: _SupportsSetEndian[_OT]) -> _OT: ...


_VT = TypeVar("_VT", default=NoneType)


class _OptionLike(Protocol[_VT]):
    name: str
    value: _VT | None


class _ArrayFactoryLike(Protocol[_IT]):
    def __call__(self, __value: Iterable[_IT]) -> Collection[_IT]: ...


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
    "_SwitchLambda",
    "_SupportsBits",
    "_ContainsBits",
    "_ArrayFactoryLike",
    "_OptionLike",
    "_ArchLike",
]
