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
from io import IOBase
from typing import Protocol, runtime_checkable
from typing import Any, Optional, Union, Callable

#: Type alias for IOBase to indicate a stream type
_StreamType = IOBase
_StreamFactory = Callable[[], _StreamType]

_GreedyType = type(...)
_PrefixedType = slice


@runtime_checkable
class _ContextLike(Protocol):
    """
    A dictionary-like object used as a context for packing and unpacking.

    It allows direct attribute access and modification.
    """

    def __context_getattr__(self, path: str) -> Any:
        pass

    def __context_setattr__(self, path: str, value: Any) -> None:
        pass

    @property
    def _root(self):
        pass

    def __getitem__(self, key: str) -> Any:
        pass

    def __setitem__(self, key: str, value: Any) -> None:
        pass

    def get(self, key: str, default: Any | None = None) -> Any:
        pass


@runtime_checkable
class _ContextLambda(Protocol):
    """
    An abstract base class for a lambda function that takes a _ContextLike
    object as an argument.
    """

    def __call__(self, context: _ContextLike) -> Any:
        pass


@runtime_checkable
class _SupportsActionUnpack(Protocol):
    def __action_pack__(self, context: _ContextLike) -> None:
        pass


@runtime_checkable
class _SupportsActionPack(Protocol):
    def __action_unpack__(self, context: _ContextLike) -> None:
        pass


@runtime_checkable
class _SupportsPack(Protocol):
    """
    An abstract base class for objects that support packing data into a binary stream.
    """

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        pass


@runtime_checkable
class _SupportsUnpack(Protocol):
    """
    An abstract base class for objects that support unpacking data from a binary stream.
    """

    def __unpack__(self, context: _ContextLike) -> Any:
        pass


@runtime_checkable
class _SupportsSize(Protocol):
    """
    An abstract base class for objects that support determining the size of packed data.
    """

    def __size__(self, context: _ContextLike) -> int:
        return 0


@runtime_checkable
class _StructLike(Protocol):
    """
    An abstract base class for struct-like objects that can be packed, unpacked, and have a size.
    """

    def __size__(self, context: _ContextLike) -> int:
        return 0

    def __unpack__(self, context: _ContextLike) -> Any:
        pass

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        pass


@runtime_checkable
class _SupportsType(Protocol):
    def __type__(self) -> Optional[Union[type, str]]:
        pass


class _ContainsStruct(Protocol):
    """
    An abstract base class indicating that a class contains a _StructLike object.
    """

    __struct__: _StructLike


@runtime_checkable
class _SwitchLike(Protocol):
    """
    An abstract base class for a switch-like object that generates a _StructLike
    based on a value and context.
    """

    @abstractmethod
    def __call__(self, value: Any, context: _ContextLike, **kwds) -> _StructLike:
        pass


@runtime_checkable
class _SupportsBits(Protocol):
    def __bits__(self) -> int: ...


@runtime_checkable
class _ContainsBits(Protocol):
    __bits__: int


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
