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
from typing import Dict, Any, Optional, Union, Callable

#: Type alias for IOBase to indicate a stream type
_StreamType = IOBase
_StreamFactory = Callable[[], _StreamType]

_GreedyType = type(...)
_PrefixedType = slice
_ContextPathStr = str


@runtime_checkable
class _ContextLike(Protocol):
    """
    A dictionary-like object used as a context for packing and unpacking.

    It allows direct attribute access and modification.
    """

    @abstractmethod
    def __context_getattr__(self, path: str) -> Any:
        pass

    # TODO
    @abstractmethod
    def __context_setattr__(self, path: str, value: Any) -> None:
        pass

    @property
    @abstractmethod
    def _root(self) -> Optional["_ContextLike"]:
        pass

    @abstractmethod
    def __getitem__(self, key: str) -> Any:
        pass

    @abstractmethod
    def __setitem__(self, key: str, value: Any) -> None:
        pass


@runtime_checkable
class _ContextLambda(Protocol):
    """
    An abstract base class for a lambda function that takes a _ContextLike object as an argument.
    """

    @abstractmethod
    def __call__(self, context: _ContextLike) -> Any:
        pass


@runtime_checkable
class _Action(Protocol):
    @abstractmethod
    def __action_pack__(self, context: _ContextLike) -> None:
        pass

    @abstractmethod
    def __action_unpack__(self, context: _ContextLike) -> None:
        pass


@runtime_checkable
class _SupportsPack(Protocol):
    """
    An abstract base class for objects that support packing data into a binary stream.
    """

    @abstractmethod
    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        pass


@runtime_checkable
class _SupportsUnpack(Protocol):
    """
    An abstract base class for objects that support unpacking data from a binary stream.
    """

    @abstractmethod
    def __unpack__(self, context: _ContextLike):
        pass


@runtime_checkable
class _SupportsSize(Protocol):
    """
    An abstract base class for objects that support determining the size of packed data.
    """

    @abstractmethod
    def __size__(self, context: _ContextLike) -> int:
        pass


@runtime_checkable
class _StructLike(Protocol):
    """
    An abstract base class for struct-like objects that can be packed, unpacked, and have a size.
    """

    @abstractmethod
    def __size__(self, context: _ContextLike) -> int:
        pass

    @abstractmethod
    def __unpack__(self, context: _ContextLike):
        pass

    @abstractmethod
    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        pass

    def __type__(self) -> Optional[Union[type, str]]:
        pass


class _ContainsStruct(Protocol):
    """
    An abstract base class indicating that a class contains a _StructLike object.
    """

    __struct__: _StructLike


class _EnumLike(Protocol):
    """
    An abstract base class for enum-like objects with a value, name, and mappings.
    """

    value: Any
    name: str
    _member_map_: Dict[str, "_EnumLike"]
    _value2member_map_: Dict[Any, "_EnumLike"]


@runtime_checkable
class _Switch(Protocol):
    """
    An abstract base class for a switch-like object that generates a _StructLike
    based on a value and context.
    """

    @abstractmethod
    def __call__(self, value: Any, context: _ContextLike, **kwds) -> _StructLike:
        pass


# TODO: place this somewhere else
STRUCT_FIELD = "__struct__"


def hasstruct(obj: Any) -> bool:
    """
    Check if the given object has a structure attribute.

    :param obj: The object to check.
    :return: True if the object has a structure attribute, else False.
    """
    cls_dict = getattr(obj.__class__ if not isinstance(obj, type) else obj, "__dict__")
    return STRUCT_FIELD in cls_dict


def getstruct(obj: Any, /, __default: Any = None) -> _StructLike | None:
    """
    Get the structure attribute of the given object.

    :param obj: The object to get the structure attribute from.
    :return: The structure attribute of the object.
    """
    obj = obj.__class__ if not isinstance(obj, type) else obj
    cls_dict = getattr(obj, "__dict__", None)
    if cls_dict is None:
        return getattr(obj, "__struct__", None)

    return cls_dict.get(STRUCT_FIELD, __default)


def typeof(struct: Union[_StructLike, _ContainsStruct]) -> object:
    if hasstruct(struct):
        struct = getstruct(struct)

    __type__ = getattr(struct, "__type__", None)
    if not __type__:
        return Any
    # this function must return a type
    return __type__() or Any
