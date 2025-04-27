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

from dataclasses import dataclass
from typing import Any, Optional, Set, Union


@dataclass(init=False)
class Flag:
    """Simple customizable user-flag."""

    name: str
    """The name of this flag"""

    value: Optional[Any] = None
    """
    Optional configuration value.
    """

    def __init__(self, name: str, value: Optional[Any] = None) -> None:
        self.name = name
        self.value = value
        self._hash_ = hash(name)

    def __hash__(self) -> int:
        """
        Custom hash method based on the flag's name.

        :return: The hash value.
        """
        return self._hash_


#: Defaults that will be applied to **all** structs.
GLOBAL_STRUCT_OPTIONS: Set[Flag] = set()

#: Defaults that will be applied on **all** unions.
GLOBAL_UNION_OPTIONS: Set[Flag] = set()

#: Default field flags that will be applied on **all** fields.
GLOBAL_FIELD_FLAGS: Set[Flag] = set()

#: Default field flags that will be applied on **all** bit-fields.
GLOBAL_BITFIELD_FLAGS: Set[Flag] = set()


def configure(base: Set[Flag], *flags: Flag) -> None:
    """
    Update the base set of flags with additional flags.

    :param base: The base set of flags.
    :param flags: Additional flags to be added.
    """
    base.update(flags)


def set_struct_flags(*flags: Flag, with_union: bool = False) -> None:
    """
    Set default flags for structs.

    :param flags: Flags to be set.
    :param with_union: Whether to include the flags for unions as well.
    """
    configure(GLOBAL_STRUCT_OPTIONS, *flags)
    if with_union:
        configure(GLOBAL_UNION_OPTIONS, *flags)


def set_field_flags(*flags: Flag) -> None:
    """
    Set default flags for fields.

    :param flags: Flags to be set.
    """
    configure(GLOBAL_FIELD_FLAGS, *flags)


def set_union_flags(*flags: Flag) -> None:
    """
    Set default flags for unions.

    :param flags: Flags to be set.
    """
    configure(GLOBAL_UNION_OPTIONS, *flags)


def get_flags(obj: Any, attr: Optional[str] = None) -> Optional[Set[Flag]]:
    """
    Get the flags associated with an object.

    :param obj: The object.
    :param attr: The attribute name containing the flags (default is "flags").
    :return: The set of flags, or None if no flags are present.
    """
    return getattr(obj, attr or "flags", None)


def has_flag(flag: Union[str, Flag], obj: Any, attr: Optional[str] = None) -> bool:
    """
    Check if an object has a specific flag.

    :param flag: The flag to check, either as a string or a Flag instance.
    :param obj: The object.
    :param attr: The attribute name containing the flags (default is "flags").
    :return: True if the flag is present, False otherwise.
    """
    flags = get_flags(obj, attr)
    if not flags or not isinstance(flags, set):
        return False

    if isinstance(flag, str):
        flag = Flag(flag)
    return flag in flags


def get_flag(name: str, obj: Any, attr: Optional[str] = None) -> Optional[Flag]:
    """
    Get a specific flag associated with an object.

    :param name: The name of the flag.
    :param obj: The object.
    :param attr: The attribute name containing the flags (default is "flags").
    :return: The Flag instance if found, otherwise None.
    """
    flags = get_flags(obj, attr)
    for flag in flags or []:
        if flag.name == name:
            return flag


###############################################################################
# Default defined options
###############################################################################

# for structs and unions
S_DISCARD_UNNAMED = Flag("discard_unnamed")
S_DISCARD_CONST = Flag("discard_const")
S_UNION = Flag("union")
S_REPLACE_TYPES = Flag("replace_types")
S_EVAL_ANNOTATIONS = Flag("eval_annotations")
S_ADD_BYTES = Flag("struct.bytes_method")
S_SLOTS = Flag("struct.slots")

# for fields
F_KEEP_POSITION = Flag("keep_position")
F_DYNAMIC = Flag("dynamic")
F_SEQUENTIAL = Flag("sequential")
F_OFFSET_OVERRIDE = Flag("offset_override")

# value intentionally left blank
O_ARRAY_FACTORY = Flag("option.array_factory", value=None)
