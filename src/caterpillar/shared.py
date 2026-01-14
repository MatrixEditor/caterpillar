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
from typing import TYPE_CHECKING, overload
from typing_extensions import Final, override, TypeIs

from caterpillar.abc import (
    _ContextLambda,
    _StructLike,
    _IT,
    _OT,
    _SupportsType,
    _ContainsStruct,
)

if TYPE_CHECKING:
    from caterpillar.fields import FieldStruct

# --- Shared Concepts ---
# TODO: This section needs some docs

# additional modifies set in the root context of each operation
MODE_PACK: Final[int] = 0
MODE_UNPACK: Final[int] = 1

# REVISIT: taken from reference
#: All models annotated with either @struct or @bitfield are struct
#: containers. Thus, they store the additional class attribute `__struct__`.
#:
#: Internally, any types utilizing this attribute can be employed within a
#: struct, bitfield, or sequence definition. The type of the stored value
#: must be conforming to the _StructLike protocol.
ATTR_STRUCT: Final[str] = "__struct__"
ATTR_BYTEORDER: Final[str] = "__byteorder__"
ATTR_TYPE: Final[str] = "__type__"
ATTR_BITS: Final[str] = "__bits__"
ATTR_SIGNED: Final[str] = "__signed__"
ATTR_TEMPLATE: Final[str] = "__template__"

# TODO: add to reference
# NEW CONCEPT: Actions
# An annotation that is equipped with an action attribute indicates that
# the struct will execute this very action instead of parsing the field.
#
# PROPOSAL:
#   For instance, an action could be used to install an IOHook on the
#   current stream (checksum or hash calculation).
#
#       class MyAction:
#           def __action__(self, context: _ContextLike) -> None:
#               ...
#
#       @struct
#       class MyStruct:
#           any_name: MyAction()
#
#   The action will be executed before the next field is parsed and won't
#   be stored in the model of the struct.
ATTR_ACTION_PACK: Final[str] = "__action_pack__"
ATTR_ACTION_UNPACK: Final[str] = "__action_unpack__"


def identity(value: _OT) -> "_ContextLambda[_OT]":
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
    def is_action(obj: object) -> bool:
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
