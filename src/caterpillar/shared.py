# Copyright (C) MatrixEditor 2023-2024
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
from typing import Callable
from caterpillar.abc import _ContextLike

# --- Shared Concepts ---
# TODO: This section need some docs

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
ATTR_ACTION = "__action__"


class Action:
    """
    A class representing an action to be executed during the parsing or processing
    of a struct. This is used for cases where a field requires an operation to be
    performed instead of directly storing data.

    An action can be used to execute custom logic (such as modifying the IO stream)
    before the next field is processed. For example, it could be used to trigger
    checksum or hash calculations before reading a struct field.

    Example:

    >>> def checksum_action(context: _ContextLike) -> None:
    ...     # This action could perform some checksum or logging logic
    ...     pass
    ...
    >>> @struct
    ... class MyStruct:
    ...     some_field: Bytes(10)
    ...     checksum: Action(checksum_action)

    In this example, the `checksum` field is an action, and the `checksum_action`
    will be invoked before the `some_field` field is parsed.

    The action itself is not stored as part of the struct's model; it merely runs
    during struct processing.

    :param run: The callable that will be executed when the action is triggered.
    :type run: Callable[[_ContextLike], None]
    """

    __slots__ = (ATTR_ACTION,)

    def __init__(self, run: Callable[[_ContextLike], None]) -> None:
        if not callable(run):
            raise TypeError("Action must be callable")
        self.__action__ = run

    def __repr__(self) -> str:
        """
        Return a string representation of the action, showing its callable name
        and location.

        :return: A string representation of the action.
        :rtype: str
        """
        return f"Action({self.__action__.__qualname__})"
