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
# pyright: reportPrivateUsage=false
"""
Module containing shared constants and utility functions for managing
and processing structs.

This module defines a set of constants and functions used across different
operations involving structs, bitfields, and related concepts. It includes
key attributes for managing struct definitions, mode constants for packing
/unpacking operations, and action handling for custom processing.

The module introduces the concept of "Actions", which are used to define
custom behavior that should be executed before parsing a struct field (e.g.,
installing IO hooks for checksums or hash calculations). Actions are
represented by classes with `__action_XX` methods.

Usage Example:
  To define a struct that executes a custom action before parsing a field:

  >>> class MyAction:
  >>>     def __action_unpack__(self, context: _ContextLike) -> None:
  >>>         ...
  >>>
  >>> @struct
  >>> class MyStruct:
  >>>     any_name: MyAction()

In this case, the action will be executed before parsing any subsequent fields
and won't be stored as part of the struct model.
"""

from typing import TYPE_CHECKING, overload
from typing_extensions import Final, Literal, override, TypeIs

from caterpillar.abc import (
    _ContextLambda,
    _StructLike,
    _IT,
    _OT,
    _SupportsType,
    _ContainsStruct,
    _ActionLike,
)

if TYPE_CHECKING:
    from caterpillar.fields import FieldStruct

# --- Shared Concepts ---
# TODO: This section needs some docs

# Constants defining packing/unpacking modes
MODE_PACK: Literal[0] = 0
"""Constant representing packing mode."""
MODE_UNPACK: Literal[1] = 1
"""Constant representing unpacking mode."""

# Constants defining struct-related attributes
ATTR_STRUCT: Final[str] = "__struct__"
"""
All models annotated with either ``@struct`` or ``@bitfield`` are struct
containers. Thus, they store the additional class attribute :code:`__struct__`.

Internally, any types utilizing this attribute can be employed within a
struct, bitfield, or sequence definition. The type of the stored value
must be conforming to the :class:`_StructLike` protocol.

.. versionchanged:: 2.5.0
    This attribute is now used when callung :func:`getstruct` or :func:`hasstruct`.
"""

ATTR_BYTEORDER: Final[str] = "__byteorder__"
"""Attribute representing the byte order of a struct.

.. versionadded:: 2.5.0
    Moved from *caterpillar.byteorder*.
"""

ATTR_TYPE: Final[str] = "__type__"
"""Attribute that stores the type of the struct.

.. versionadded:: 2.5.0
"""

ATTR_BITS: Final[str] = "__bits__"
"""Attribute representing the number of bits in a struct.

.. versionadded:: 2.5.0
    Moved from *caterpillar.model._bitfield*.
"""

ATTR_SIGNED: Final[str] = "__signed__"
"""Attribute that marks a struct as signed.

.. versionadded:: 2.5.0
    Moved from *caterpillar.model._bitfield*.
"""

ATTR_TEMPLATE: Final[str] = "__template__"
"""Attribute that provides the template for the struct.

.. versionadded:: 2.5.0
    Moved from *caterpillar.model._template*.
"""

ATTR_PACK: Final[str] = "__pack__"
"""Attribute that defines packing behavior for the struct.

.. versionadded:: 2.8.0
"""
ATTR_UNPACK: Final[str] = "__unpack__"
"""Attribute that defines unpacking behavior for the struct.

.. versionadded:: 2.8.0
"""

# Constants for actions during packing and unpacking
ATTR_ACTION_PACK: Final[str] = "__action_pack__"
"""Attribute indicating an action to be executed during packing.

.. versionadded:: 2.4.0
"""

ATTR_ACTION_UNPACK: Final[str] = "__action_unpack__"
"""Attribute indicating an action to be executed during unpacking.

.. versionadded:: 2.4.0
"""


def constval(value: _OT) -> "_ContextLambda[_OT]":
    """Returns a lambda that returns a constant value when invoked.

    :param value: The constant value to be returned by the lambda.
    :type value: _OT
    :return: A lambda function that, when called, returns the given constant value.
    :rtype: _ContextLambda[_OT]
    """
    return lambda context: value


class Action:
    """
    A class representing an action to be executed during the parsing or processing
    of a struct. This is used for cases where a field requires an operation to be
    performed instead of directly storing data.

    An action can be used to execute custom logic (such as modifying the IO stream)
    before the next field is processed. For example, it could be used to trigger
    checksum or hash calculations before reading a struct field.

    There are two types of actions:

    1. **Packing actions**: These actions are triggered before packing the data into the struct (i.e., before serializing or encoding).
    2. **Unpacking actions**: These actions are triggered before unpacking the data from the struct (i.e., before deserializing or decoding).

    Example:

    >>> def checksum_action(context: _ContextLike) -> None:
    ...     # This action could perform some checksum or logging logic
    ...     pass
    ...
    >>> @struct
    ... class MyStruct:
    ...     some_field: Bytes(10)
    ...     checksum: Action(checksum_action) # runs only when packing

    In this example, the `checksum` field is an action, and the `checksum_action`
    will be invoked before the `some_field` field is parsed.

    The action itself is not stored as part of the struct's model; it merely runs
    during struct processing.

    :param pack: The callable that will be executed before packing the struct (optional).
    :type pack: _ContextLambda | None
    :param unpack: The callable that will be executed before unpacking the struct (optional).
    :type unpack: _ContextLambda | None
    """

    __slots__: tuple[str, str] = (ATTR_ACTION_PACK, ATTR_ACTION_UNPACK)

    def __init__(
        self,
        pack: _ContextLambda[None] | None = None,
        unpack: _ContextLambda[None] | None = None,
        both: _ContextLambda[None] | None = None,
    ) -> None:
        self.__action_pack__: _ContextLambda[None] | None = pack
        self.__action_unpack__: _ContextLambda[None] | None = unpack
        if both is not None:
            self.__action_pack__ = self.__action_unpack__ = both

    @override
    def __repr__(self) -> str:
        """
        Return a string representation of the action, showing its callable name
        and location.

        If only one of the action types is provided (either packing or unpacking),
        the corresponding action type (`PackAction` or `UnpackAction`) is displayed.

        :return: A string representation of the action.
        :rtype: str
        """
        name = "Action"
        if self.__action_pack__ and not self.__action_unpack__:
            name = "PackAction"
            return f"{name}({self.__action_pack__.__qualname__})"

        elif self.__action_unpack__ and not self.__action_pack__:
            name = "UnpackAction"
            return f"{name}({self.__action_unpack__.__qualname__})"

        if not self.__action_pack__ and not self.__action_unpack__:
            return name

        if self.__action_pack__ is self.__action_unpack__:
            return f"{name}({self.__action_pack__.__qualname__})"

        return f"{name}({self.__action_pack__.__qualname__}, {self.__action_unpack__.__qualname__})"

    @staticmethod
    def is_action(obj: object) -> TypeIs[_ActionLike]:
        """
        Checks if the given object is an instance of an `Action` class,
        based on the presence of the `__action_pack__` or `__action_unpack__` attributes.

        :param obj: The object to check.
        :type obj: Any
        :return: True if the object has either a `__action_pack__` or `__action_unpack__` attribute, indicating it is an action.
        :rtype: bool
        """
        return any(
            getattr(obj, attr, None) for attr in (ATTR_ACTION_PACK, ATTR_ACTION_UNPACK)
        )


def hasstruct(obj: object) -> TypeIs[_ContainsStruct]:
    """
    Check if the given object has a structure attribute.

    :param obj: The object to check.
    :return: True if the object has a structure attribute, else False.
    """
    return hasattr(obj.__class__ if not isinstance(obj, type) else obj, ATTR_STRUCT)


@overload
def getstruct(
    obj: type[_IT],
    /,
    __default: None = None,
) -> "FieldStruct[_IT, _IT]": ...
@overload
def getstruct(
    obj: _ContainsStruct[_IT, _OT],
    /,
    __default: None = None,
) -> _StructLike[_IT, _OT]: ...
@overload
def getstruct(
    obj: object,
    /,
    __default: _StructLike | None = None,
) -> "_StructLike | FieldStruct | None": ...
def getstruct(
    obj: object, /, __default: _StructLike | None = None
) -> "_StructLike | FieldStruct | None":
    """
    Get the structure attribute of the given object.

    :param obj: The object to get the structure attribute from.
    :return: The structure attribute of the object.
    """
    obj = obj.__class__ if not isinstance(obj, type) else obj
    return getattr(obj, ATTR_STRUCT, __default)


def typeof(struct: _StructLike | _SupportsType | _ContainsStruct | object) -> type:
    """Returns the type of a given struct or object, checking for a custom type annotation.

    If the given object has a `__type__` attribute, this function returns that type. If not, it
    returns the object's default type. If the type cannot be resolved, the function defaults to
    returning `object`.

    :param struct: The struct or object whose type is to be resolved.
    :type struct: _StructLike | _SupportsType | _ContainsStruct | object
    :return: The resolved type of the struct or object.
    :rtype: type
    """
    if hasstruct(struct):
        struct = getstruct(struct) or struct

    __type__ = getattr(struct, ATTR_TYPE, None)
    if not __type__:
        return object
    # this function must return a type
    rtype = object
    try:
        rtype = __type__()  # pyright: ignore[reportAny]
    except NotImplementedError:
        pass

    return rtype if rtype and rtype != NotImplemented else object
