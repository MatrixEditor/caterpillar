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
from dataclasses import dataclass
from typing import Generic
from typing_extensions import Final, override

from caterpillar.abc import _OptionLike, _VT, _ArrayFactoryLike


@dataclass(init=False, eq=False)
class Flag(Generic[_VT]):
    """Simple customizable user-flag."""

    name: str
    """The name of this flag"""

    value: _VT | None = None
    """
    Optional configuration value.
    """

    def __init__(self, name: str, value: _VT | None = None) -> None:
        self.name = name
        self.value = value
        self._hash_: int = hash(name)

    @override
    def __hash__(self) -> int:
        """
        Custom hash method based on the flag's name.

        :return: The hash value.
        """
        return self._hash_

    @override
    def __eq__(self, value: object, /) -> bool:
        # custom check to allow c_Option objects to be used
        return getattr(value, "name", None) == self.name  # pyright: ignore[reportAny]


#: Defaults that will be applied to **all** structs.
GLOBAL_STRUCT_OPTIONS: set[_OptionLike] = set()

#: Defaults that will be applied on **all** unions.
GLOBAL_UNION_OPTIONS: set[_OptionLike] = set()

#: Default field flags that will be applied on **all** fields.
GLOBAL_FIELD_FLAGS: set[_OptionLike] = set()

#: Default field flags that will be applied on **all** bit-fields.
GLOBAL_BITFIELD_FLAGS: set[_OptionLike] = set()


def configure(base: set[_OptionLike], *flags: _OptionLike) -> None:
    """
    Update the base set of flags with additional flags.

    :param base: The base set of flags.
    :param flags: Additional flags to be added.
    """
    base.update(flags)


def set_struct_flags(*flags: _OptionLike, with_union: bool = False) -> None:
    """
    Set default flags for structs.

    :param flags: Flags to be set.
    :param with_union: Whether to include the flags for unions as well.
    """
    configure(GLOBAL_STRUCT_OPTIONS, *flags)
    if with_union:
        configure(GLOBAL_UNION_OPTIONS, *flags)


def set_field_flags(*flags: _OptionLike) -> None:
    """
    Set default flags for fields.

    :param flags: Flags to be set.
    """
    configure(GLOBAL_FIELD_FLAGS, *flags)


def set_union_flags(*flags: _OptionLike) -> None:
    """
    Set default flags for unions.

    :param flags: Flags to be set.
    """
    configure(GLOBAL_UNION_OPTIONS, *flags)


def get_flags(obj: object, attr: str | None = None) -> list[_OptionLike] | None:
    """
    Get the flags associated with an object.

    :param obj: The object.
    :param attr: The attribute name containing the flags (default is "flags").
    :return: The set of flags, or None if no flags are present.
    """
    return getattr(obj, attr or "flags", None)


def has_flag(flag: _OptionLike[_VT], obj: object, attr: str | None = None) -> bool:
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


def get_flag(
    name: str, obj: object, attr: str | None = None
) -> _OptionLike[_VT] | None:
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
            return flag  # pyright: ignore[reportReturnType]


###############################################################################
# Default defined options
###############################################################################

# for structs and unions
S_DISCARD_UNNAMED: Final[Flag] = Flag("struct.discard_unnamed")
S_DISCARD_CONST: Final[Flag] = Flag("struct.discard_const")
S_UNION: Final[Flag] = Flag("struct.union")
S_REPLACE_TYPES: Final[Flag] = Flag("struct.replace_types")
S_EVAL_ANNOTATIONS: Final[Flag] = Flag("struct.eval_annotations")
S_ADD_BYTES: Final[Flag] = Flag("struct.bytes_method")
S_SLOTS: Final[Flag] = Flag("struct.slots")

# for fields
F_KEEP_POSITION: Final[Flag] = Flag("field.keep_position")
F_DYNAMIC: Final[Flag] = Flag("field.dynamic")
F_SEQUENTIAL: Final[Flag] = Flag("field.sequential")
F_OFFSET_OVERRIDE: Final[Flag] = Flag("field.offset_override")

# value intentionally left blank
O_ARRAY_FACTORY: Flag[_ArrayFactoryLike] = Flag("option.array_factory", value=None)

# bitfield options
B_OVERWRITE_ALIGNMENT: Final[Flag] = Flag("bitfield.overwrite_alignment")
B_GROUP_END: Final[Flag] = Flag("bitfield.group.end")
B_GROUP_NEW: Final[Flag] = Flag("bitfield.group.new")
B_GROUP_KEEP: Final[Flag] = Flag("bitfield.group.keep")
B_NO_AUTO_BOOL: Final[Flag] = Flag("bitfield.no_auto_bool")
