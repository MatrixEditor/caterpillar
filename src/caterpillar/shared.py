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
from typing import Any
from caterpillar.abc import _ContextLambda

# --- Shared Concepts ---
# TODO: This section needs some docs

# additional modifies set in the root context of each operation
MODE_PACK = 0
MODE_UNPACK = 1

# REVISIT: taken from reference
#: All models annotated with either @struct or @bitfield are struct
#: containers. Thus, they store the additional class attribute `__struct__`.
#:
#: Internally, any types utilizing this attribute can be employed within a
#: struct, bitfield, or sequence definition. The type of the stored value
#: must be conforming to the _StructLike protocol.
ATTR_STRUCT = "__struct__"
ATTR_BYTEORDER = "__byteorder__"
ATTR_TYPE = "__type__"
ATTR_BITS = "__bits__"
ATTR_SIGNED = "__signed__"
ATTR_TEMPLATE = "__template__"

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
ATTR_ACTION_PACK = "__action_pack__"
ATTR_ACTION_UNPACK = "__action_unpack__"


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

    __slots__ = (ATTR_ACTION_PACK, ATTR_ACTION_UNPACK)

    def __init__(self, pack=None, unpack=None, both=None) -> None:
        self.__action_pack__ = pack
        self.__action_unpack__ = unpack
        if both is not None:
            self.__action_pack__ = self.__action_unpack__ = both

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
    def is_action(obj: Any) -> bool:
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


def hasstruct(obj) -> bool:
    """
    Check if the given object has a structure attribute.

    :param obj: The object to check.
    :return: True if the object has a structure attribute, else False.
    """
    cls_dict = getattr(obj.__class__ if not isinstance(obj, type) else obj, "__dict__")
    return ATTR_STRUCT in cls_dict


def getstruct(obj, /, __default=None):
    """
    Get the structure attribute of the given object.

    :param obj: The object to get the structure attribute from.
    :return: The structure attribute of the object.
    """
    obj = obj.__class__ if not isinstance(obj, type) else obj
    cls_dict = getattr(obj, "__dict__", None)
    if cls_dict is None:
        return getattr(obj, ATTR_STRUCT, None)

    return cls_dict.get(ATTR_STRUCT, __default)


def typeof(struct):
    if hasstruct(struct):
        struct = getstruct(struct)

    __type__ = getattr(struct, ATTR_TYPE, None)
    if not __type__:
        return Any
    # this function must return a type
    return __type__() or Any
