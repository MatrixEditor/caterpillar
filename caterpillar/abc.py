# Copyright (C) MatrixEditor 2023
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
from __future__ import annotations

from abc import ABC, abstractmethod
from io import IOBase
from typing import Dict, Any, Optional, Union, Callable

#: Type alias for IOBase to indicate a stream type
_StreamType = IOBase
_StreamFactory = Callable[[], _StreamType]

class _ContextLike(dict):
    """
    A dictionary-like object used as a context for packing and unpacking.

    It allows direct attribute access and modification.
    """

    @abstractmethod
    def __setattr__(self, key: str, value) -> None:
        pass

    @abstractmethod
    def __getattribute__(self, key: str):
        pass

    @abstractmethod
    def root(self) -> Optional[_ContextLike]:
        pass


class _ContextLambda(ABC):
    """
    An abstract base class for a lambda function that takes a _ContextLike object as an argument.
    """

    @abstractmethod
    def __call__(self, context: _ContextLike, **kwds):
        pass


class _SupportsPack(ABC):
    """
    An abstract base class for objects that support packing data into a binary stream.
    """

    @abstractmethod
    def __pack__(self, obj, stream: _StreamType, context: _ContextLike) -> None:
        pass


class _SupportsUnpack(ABC):
    """
    An abstract base class for objects that support unpacking data from a binary stream.
    """

    @abstractmethod
    def __unpack__(self, stream: _StreamType, context: _ContextLike):
        pass


class _SupportsSize(ABC):
    """
    An abstract base class for objects that support determining the size of packed data.
    """

    @abstractmethod
    def __size__(self, context: _ContextLike) -> int:
        pass


class _StructLike(_SupportsPack, _SupportsUnpack, _SupportsSize):
    """
    An abstract base class for struct-like objects that can be packed, unpacked, and have a size.
    """

    def __type__(self) -> Optional[type]:
        pass


class _ContainsStruct(ABC):
    """
    An abstract base class indicating that a class contains a _StructLike object.
    """

    __struct__: _StructLike


class _EnumLike(ABC):
    """
    An abstract base class for enum-like objects with a value, name, and mappings.
    """

    value: Any
    name: str
    _member_map_: Dict[str, _EnumLike]
    _value2member_map_: Dict[Any, _EnumLike]


class _Switch(ABC):
    """
    An abstract base class for a switch-like object that generates a _StructLike based on a value and context.
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
    return bool(getattr(obj, STRUCT_FIELD, None))


def getstruct(obj: Any) -> _StructLike:
    """
    Get the structure attribute of the given object.

    :param obj: The object to get the structure attribute from.
    :return: The structure attribute of the object.
    """
    return getattr(obj, STRUCT_FIELD)


def typeof(struct: Union[_StructLike, _ContainsStruct]) -> type:
    if hasstruct(struct):
        struct = getstruct(struct)

    __type__ = getattr(struct, "__type__", None)
    if not __type__:
        return Any
    # this function must return a type
    return __type__() or Any
