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


def get_flags(obj: object, attr: str | None = None) -> list[_OptionLike]:
    """
    Get the flags associated with an object.

    .. versionchanged:: 2.8.0
        now always returns a list

    :param obj: The object.
    :param attr: The attribute name containing the flags (default is "flags").
    :return: The set of flags, or None if no flags are present.
    """
    return list(getattr(obj, attr or "flags", None) or [])


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
"""
When enabled, this option discards all *unnamed* fields from the final unpacked result.
An *unnamed* field must follow the convention:

```bnf
<unnamed> := '_' [0-9]*
```
This allows you to include padding or other non-essential fields without polluting
the output. For example:

>>> schema = Seq({
...     "a": uint8,
...     "_": padding[10]
... }, options={opt.S_DISCARD_UNNAMED})
>>> data = b"\xff" + bytes(10)
>>> unpack(schema, data)
{'a': 255}
>>> pack(_, schema)
b'\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
"""

S_SLOTS: Final[Flag] = Flag("struct.slots")
"""
When enabled, this option generates a struct class with a `__slots__` declaration.
Using `__slots__` significantly reduces the per-object memory overhead by preventing
the creation of an instance `__dict__`.
"""


S_REPLACE_TYPES: Final[Flag] = Flag("struct.replace_types")
"""
Replaces field types in the class annotations with their native Python equivalents.
This option is primarily intended for documentation purposes. It removes all
:class:`caterpillar.fields.Field` instances from annotations. For example:

>>> @struct
>>> class Format:
...     a: uint8_t
...     b: String(10)
...     c: uuid_t
...
>>> # Enable type replacement globally
>>> opt.set_struct_flags(opt.S_REPLACE_TYPES)
>>> # Or apply it directly:
>>> @struct(options={opt.S_REPLACE_TYPES})

Comparison of annotations:

>>> Format.__annotations__ # Without replacement
{'a': <FormatField(int) 'B'>, 'b': <String>, 'c': <Uuid>}
>>> Format.__annotations__ # With replacement
{'a': <class 'int'>, 'b': <class 'str'>, 'c': <class 'uuid.UUID'>}
"""

S_EVAL_ANNOTATIONS: Final[Flag] = Flag("struct.eval_annotations")
"""
Ensures that annotations are evaluated at runtime if you use
`from __future__ import annotations`. When enabled, stringified annotations
are evaluated before analysis.
"""

S_UNION: Final[Flag] = Flag("struct.union")
S_ADD_BYTES: Final[Flag] = Flag("struct.bytes_method")
S_DISCARD_CONST: Final[Flag] = Flag("struct.discard_const")

# for fields
F_KEEP_POSITION: Final[Flag] = Flag("field.keep_position")
"""
When enabled, this option retains the position information of each field in the
serialized data. This is the default behavior.
"""

F_DYNAMIC: Final[Flag] = Flag("field.dynamic")
"""
Marks the field as dynamic, indicating that its size or format is determined at
runtime rather than being statically defined. This is used internally to support
advanced features like variable-length fields.

**Deprecated since 2.8.0**
"""

F_SEQUENTIAL: Final[Flag] = Flag("field.sequential")
"""
Allows you to override the calculated offset for this field within its parent
structure. This means, the offset used by the `struct.__matmul__`
operation will be used from here on.

**Deprecated since 2.8.0**
"""

F_OFFSET_OVERRIDE: Final[Flag] = Flag("field.offset_override")

# value intentionally left blank
O_ARRAY_FACTORY: Flag[_ArrayFactoryLike] = Flag("option.array_factory", value=None)
"""
Specifies a factory function or class for creating array instances. This allows you
to replace the default array type with a more efficient or specialized implementation.
For example, you can use `numpy.ndarray` for large numeric arrays to reduce memory
usage:

>>> from caterpillar.options import O_ARRAY_FACTORY
>>> from numpy import array
>>> # Set the array factory globally
>>> O_ARRAY_FACTORY.value = array

With this configuration, unpacked arrays will use the specified factory, potentially
leading to significant memory savings. The following table demonstrates the memory
footprint of unpacked objects under different configurations:
"""

# bitfield options
B_OVERWRITE_ALIGNMENT: Final[Flag] = Flag("bitfield.overwrite_alignment")
"""
Replaces the current alignment with the alignment explicitly defined by the field.
This option is applicable only to fields within a bit-field class.

For example, the following structure overrides the default alignment of 8 bits
with a 32-bit alignment for the specified field:

.. code-block:: python

>>> @bitfield
... class Format:
...     # Override alignment from 8 bits to 32 bits
...     a: f[int, 4 - uint32 | B_OVERWRITE_ALIGNMENT]
...
"""

B_GROUP_END: Final[Flag] = Flag("bitfield.group.end")
"""
Adds the annotated field to the current bit-field group and immediately aligns
the group's total size according to the active alignment constraints.
This option is applicable only to fields.

For example, to avoid automatic alignment to the next multiple of 16 bits:

.. code-block:: python

>>> @bitfield
... class Format:
...     a1: int4_t
...     a2: int3_t
...     # Prevent automatic alignment to 16 bits:
...     a3: f[int, (1, B_GROUP_END)]
...     b1: int1_t
...     ...
"""

B_GROUP_NEW: Final[Flag] = Flag("bitfield.group.new")
"""
Finalizes the current bit-field group by aligning it, then starts a new group
and adds the annotated field to this new group.
This option is applicable only to fields.

Example usage where a new group is started with its own alignment:

>>> @bitfield
... class Format:
...     a1: int4_t
...     a2: int4_t
...     # Finalize current group and start new one with 8-bit alignment:
...     b1: f[int, ] (1, B_GROUP_NEW)]
"""

B_GROUP_KEEP: Final[Flag] = Flag("bitfield.group.keep")
"""
*Applicable to classes only.*

When applied at the class level, this option instructs the bit-field structure
to preserve existing group alignments throughout parsing and packing.
It affects how alignment statements are interpreted within the class body.
"""

B_NO_AUTO_BOOL: Final[Flag] = Flag("bitfield.no_auto_bool")
"""
*Applicable only to classes.*

Prevents the automatic assignment of a boolean type factory for fields
that are exactly one bit in size. By default, one-bit fields are treated
as boolean values; enabling this option disables that behavior, preserving
the raw integer representation instead.
"""
