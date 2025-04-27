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
from typing import Any, Callable
from caterpillar.abc import _ContextLike

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
    :type pack: Callable[[_ContextLike], None] | None
    :param unpack: The callable that will be executed before unpacking the struct (optional).
    :type unpack: Callable[[_ContextLike], None] | None
    """

    __slots__ = (ATTR_ACTION_PACK, ATTR_ACTION_UNPACK)

    def __init__(
        self,
        pack: Callable[[_ContextLike], None] | None = None,
        unpack: Callable[[_ContextLike], None] | None = None,
    ) -> None:
        self.__action_pack__ = pack
        self.__action_unpack__ = unpack

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
