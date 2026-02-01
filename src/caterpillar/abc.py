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
# pyright: reportExplicitAny=false, reportAny=false
from collections.abc import Iterable, Collection
from io import IOBase
from types import EllipsisType, NoneType
from typing import (
    Any,
    Callable,
    Protocol,
    runtime_checkable,
)
from typing_extensions import Final, TypeVar

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
    A protocol for context-like objects that provides methods and attributes
    for working with context variables.

    >>> context: _ContextLike = Context(a=1, b="2")
    >>> # attribute-style access
    >>> context.__context_getattr__("a")
    1
    >>> # dict-style access
    >>> context["b"]
    "2"

    In general, it is recommnded to use:

    - `__getitem__` when accessing 1st-level attributes directly, and
    - `__context_getattr__` when querying attributes on level 2...
    """

    @property
    def _root(self) -> "_ContextLike":
        """
        References the root context object. This attribute provides access
        to the top-level context, which can be useful for resolving global context
        variables or for operations that require awareness of the entire context hierarchy.

        :return: The root context object.
        :rtype: _ContextLike
        """
        ...

    def __context_getattr__(self, path: str) -> Any:
        """
        Retrieves a value from the context based on the given path. It is
        implementation-dependent whether nested paths are supported; by default,
        multiple path elements are separated by a single dot

        For example, given the path :code:`"foo.bar"`, the context implementation
        should first resolve the value associated with :code:`"foo"`, then retrieve
        the :code:`"bar"` attribute from that result

        :param path: A string representing the path to the desired value.
        :type path: str
        :return: The value associated with the given path.
        :rtype: Any
        """
        ...

    def __context_setattr__(self, path: str, value: Any) -> None:
        """
        Sets the value of a context variable specified by the given path.
        Similar to :meth:`__context_getattr__`, multiple path elements are
        separated by a dot by default. Implementations should resolve the
        intermediate path components and update the target variable with the
        provided value.

        For example, given the path :code:`"foo.bar"` and a value of type `int`,
        the context implementation would first check for the existence of :code:`"foo"`
        and then set its associated attribute to an integer value.

        :param path: A string representing the path to the desired value.
        :type path: str
        :param value: The value to be assigned to the specified context variable.
        :type value: Any
        """
        ...

    def __getitem__(self, key: str, /) -> Any:
        """
        Returns an item from the context based on the given index. The method is
        designed to work with strings representing attributes.

        :param key: A string representing the path to the desired value.
        :type key: str
        :return: The value associated with the given index.
        :rtype: Any
        """
        ...

    def __setitem__(self, key: str, value: Any, /) -> None:
        """
        Sets a value in the context at the specified index.The method updates the target
        attribute with the provided value.

        For example, given the path :code:`"foo.bar"` and an integer value,
        this method will update :code:`"foo"`'s associated attribute to a new integer value.

        :param key: A string representing the index of the desired value.
        :type key: str
        :param value: The value to be set at the specified index in the context.
        :type value: Any
        """
        ...

    def get(self, key: str, default: Any | None = None, /) -> Any:
        """
        Retrieves a value from the context based on the given index. If no
        value is found at the specified index or if the default is provided,
        the method returns the default value.

        :param key: A string representing the index of the desired value.
        :type key: str
        :param default: The default value to be returned if no value is found at
                        the specified index. Defaults to `None`.
        :type default: Any | None, optional
        :return: The value associated with the given index or the provided default.
        :rtype: Any
        """
        ...


@runtime_checkable
class _ContextLambda(Protocol[_ContextLambdaReturnT_co]):
    """
    A protocol class for a context lambda that accepts a context-like object
    and returns a result.

    :param _ContextLike: A type hint representing the context-like object.
    :type _ContextLike: Type[_ContextLike]
    :param _ContextLambdaReturnT_co: The return type of the context lambda
    :type _ContextLambdaReturnT_co: Any
    """

    def __call__(self, context: _ContextLike) -> _ContextLambdaReturnT_co: ...


_ArgType = _ContextLambda[Any] | Any


@runtime_checkable
class _SupportsActionUnpack(Protocol):
    """
    A protocol class for an action-like object that is defined to unpack data during deserialization.

    :param _ContextLike: The context-like object passed to the method.
    :type _ContextLike: Type[_ContextLike]
    """

    def __action_pack__(self, context: _ContextLike) -> None:
        """
        Unpack action for deserialization. This method is typically used for validation, verification,
        or any other operation that should run during unpacking process.
        """
        ...


@runtime_checkable
class _SupportsActionPack(Protocol):
    """
    A protocol class for an action-like object that is defined to pack data during serialization.

    :param _ContextLike: The context-like object passed to the method.
    :type _ContextLike: Type[_ContextLike]
    """

    def __action_unpack__(self, context: _ContextLike) -> None:
        """
        Pack action for serialization. This method is typically used for tasks such as calculating
        checksums or logging.
        """


_ActionLike = _SupportsActionPack | _SupportsActionUnpack


@runtime_checkable
class _SupportsPack(Protocol[_IT_contra]):
    """
    An abstract base class for objects that support packing data into a binary stream.

    .. versionchanged:: beta
        The *stream* parameter has been removed and was instead moved into the context.
    """

    def __pack__(self, obj: _IT_contra, context: _ContextLike) -> None:
        """Invoked to serialize the given object (obj) into an output stream.

        :param obj: The input object to be packed.
        :type obj: _IT_contra
        :param context: Contextual information or state needed for packing, including
                        additional parameters required by the implementation.
        :type context: _ContextLike
        :return: None
        """
        ...


@runtime_checkable
class _SupportsUnpack(Protocol[_OT_co]):
    """
    An abstract base class for objects that support unpacking data from a binary stream.
    """

    def __unpack__(self, context: _ContextLike) -> _OT_co:
        """Called to deserialize objects from an input stream.

        :param context: Contextual information or state needed for deserialization, including
                        additional parameters required by the implementation.
        :type context: _ContextLike
        :return: A deserialized object of type `_OT_co`.
        """
        ...


@runtime_checkable
class _SupportsSize(Protocol):
    """
    An abstract base class for objects that support determining the size of packed data.
    """

    def __size__(self, context: _ContextLike) -> int:
        """
        This method serves the purpose of determining the space occupied by this struct,
        expressed in bytes.

        :param context: Contextual information or state needed for size determination,
                        including additional parameters required by the implementation.
        :type context: _ContextLike
        :return: The number of bytes occupied by this struct.
        """
        ...


@runtime_checkable
class _StructLike(Protocol[_IT_contra, _OT_co]):
    """A Protocol for a Struct-Like object.

    This protocol describes the methods required to implement operations on a struct-like
    object. It defines how input objects are written to an output stream (`__pack__`),
    deserialized from an input stream (`__unpack__`), and its size is determined in bytes
    (`__size__`). Additionally, it provides a way to specify its type if necessary
    (`__type__`).
    """

    def __size__(self, context: _ContextLike) -> int:
        """Determines the space occupied by this struct, expressed in bytes.

        :param context: Contextual information or state needed for size determination,
                        including additional parameters required by the implementation.
        :type context: _ContextLike
        :return: The number of bytes occupied by this struct.
        """
        ...

    def __unpack__(self, context: _ContextLike) -> _OT_co:
        """Called to deserialize objects from an input stream.

        :param self: The protocol instance itself.
        :type self: _StructLike[_IT_contra, _OT_co]
        :param context: Contextual information or state needed for deserialization, including
                        additional parameters required by the implementation.
        :type context: _ContextLike
        :return: A deserialized object of type `_OT_co`.
        """
        ...

    def __pack__(self, obj: _IT_contra, context: _ContextLike) -> None:
        """Invoked to serialize the given object into an output stream.

        :param obj: The input object to be packed.
        :type obj: _IT_contra
        :param context: Contextual information or state needed for packing, including
                        additional parameters required by the implementation.
        :type context: _ContextLike
        """
        ...

    def __type__(self) -> type | str | None:
        """
        Configuration of *Structs* incorporates type replacement before a dataclass
        is created. This method is used to determine the type of a struct.

        :return: The type specification, defaults to `Any` if not explicitly defined.
        """
        ...


_PrefixedType = slice  # [_StructLike[int, int], NoneType, NoneType]
_LengthT = int | _PrefixedType | _GreedyType | _ContextLambda[int]


@runtime_checkable
class _SupportsType(Protocol):
    def __type__(self) -> type | str | None: ...


class _ContainsStruct(Protocol[_IT_contra, _OT]):
    """
    An abstract base class indicating that a class contains a _StructLike object.
    """

    __struct__: _StructLike[_IT_contra, _OT]


@runtime_checkable
class _SwitchLambda(Protocol):
    """
    An abstract base class for a switch-like object that generates a _StructLike
    based on a value and context.
    """

    def __call__(self, value: Any, context: _ContextLike) -> _StructLike: ...


_SwitchOptionsT = _SwitchLambda | dict[Any, Any]
"""
.. versionadded 2.8.0
"""

@runtime_checkable
class _SupportsBits(Protocol):
    def __bits__(self) -> int: ...


@runtime_checkable
class _ContainsBits(Protocol):
    __bits__: int


@runtime_checkable
class _ArchLike(Protocol):
    name: str
    ptr_size: int

    def __init__(self, name: str, ptr_size: int) -> None: ...


class _SupportsSetEndian(Protocol[_OT_co]):
    def __set_byteorder__(self, order: "_EndianLike") -> _OT_co: ...


@runtime_checkable
class _EndianLike(Protocol):
    name: Final[str]

    @property
    def ch(self) -> str: ...
    def __add__(self, other: _SupportsSetEndian[_OT]) -> _OT: ...


_VT = TypeVar("_VT", default=NoneType)


@runtime_checkable
class _OptionLike(Protocol[_VT]):
    name: str
    value: _VT | None


class _ArrayFactoryLike(Protocol[_IT]):
    def __call__(self, __value: Iterable[_IT]) -> Collection[_IT]: ...


class _ContextFactoryLike(Protocol):
    """

    .. versionadded 2.8.0
    """

    def __call__(self, **kwargs: Any) -> _ContextLike: ...


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
    "_ContextFactoryLike",
    "_ActionLike",
    "_SwitchOptionsT",
    "_LengthT",
]
