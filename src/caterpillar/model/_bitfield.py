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
import dataclasses
import enum

from collections.abc import Iterable
from typing import Any, Callable, Final, Generic, Literal
from typing_extensions import (
    ClassVar,
    Self,
    dataclass_transform,
    overload,
    override,
    TypeVar,
)
from caterpillar.fields.common import Int
from caterpillar.shared import (
    ATTR_ACTION_PACK,
    ATTR_ACTION_UNPACK,
    typeof,
    ATTR_BITS,
    ATTR_SIGNED,
)
from caterpillar.byteorder import (
    LITTLE_ENDIAN_FMT,
    O_DEFAULT_ENDIAN,
    LittleEndian,
)
from caterpillar.options import (
    B_GROUP_NEW,
    GLOBAL_BITFIELD_FLAGS,
    GLOBAL_STRUCT_OPTIONS,
    GLOBAL_UNION_OPTIONS,
    B_OVERWRITE_ALIGNMENT,
    B_GROUP_END,
    B_GROUP_KEEP,
    B_NO_AUTO_BOOL,
    Flag,
)
from caterpillar.fields import (
    Field,
    Pass,
    INVALID_DEFAULT,
)
from caterpillar.exception import StructException
from caterpillar.context import (
    CTX_FIELD,
    CTX_PATH,
    O_CONTEXT_FACTORY,
    CTX_OBJECT,
    CTX_STREAM,
    Context,
)
from caterpillar.abc import (
    _StructLike,
    _ActionLike,
    _ContextLike,
    _OptionLike,
    _ArchLike,
    _EndianLike,
)
from ._struct import (
    Struct,
    StructDefMixin,
    sizeof,
    Invisible,
)
from ._base import Sequence

_AnnotationT = int | tuple[int, ...] | Any  # pyright: ignore[reportExplicitAny]
_ModelT = TypeVar("_ModelT")

# --- Bitfield Concept ---
# NEW REVISED CONCEPT
# Each Bitfield instance maintains a sequence of bitfield groups, where each group
# contains a collection of sized fields. A bitfield group may consist of either multiple
# entries (i.e., any types that can be converted to an integral type) or a single
# _StructLike object. For example, consider the following bitfield definition:
#
#   @bitfield
#   class Format:
#       a1: 1
#       a2: 1 - boolean
#       _ : 0
#       b1: char
#       c1: uint32
#
# This Bitfield definition will generate three distinct bitfield groups (labeled here as
# groups a, b, and c). By default, bitfields use 8-bit alignment, leading to the following
# layout:
#
#       Group      Pos       Bits
#       a          0x00      8
#       b          0x01      8
#       c          0x02      32
#
# Internally, only the first group requires special bit-level parsing. The remaining groups
# (b and c) are treated as standard structures since they span full bytes or words without
# sub-byte alignment. This dynamic grouping mechanism allows leveraging full struct-like
# class definitions within bitfields.
#
# This new approach enables more complex and expressive bitfield definitions. The annotation
# syntax is therefore extended as follows:
#
#   +---------------------------------------------------+--------------------------------------+
# 1.| <name> : <bits> [ - <field> ]                     | Standard field with optional type    |
#   +---------------------------------------------------+--------------------------------------+
# 2.| <name> : 0                                        | Aligns to the next byte boundary     |
#   +---------------------------------------------------+--------------------------------------+
# 3.| <name> : <field>                                  | Struct-like field (no bits consumed) |
#   +---------------------------------------------------+--------------------------------------+
# 4.| <name> : (<field>,<factory>)                      | Field with custom type factory       |
#   +---------------------------------------------------+--------------------------------------+
# 5.| <name> : (<bits>,<factory>[,<options>])           | bits with custom type factory        |
#   |        : (<bits>,[<options>])                     | and options                          |
#   +---------------------------------------------------+--------------------------------------+
#
# Processing Rules:
#
#   Rule 1.:
#       - Default alignment is 1 byte (8 bits).
#       - If followed by a rule 2 declaration, the remaining bits in the current byte are padded.
#       - If a <field> is provided:
#           - typeof(<field>) is used to infer the factory.
#           - etbits() and sizeof() determine the field’s alignment.
#       - If a custom alignment is configured in the Bitfield constructor, inferred alignment is
#         ignored unless the field includes the B_OVERWRITE_ALIGNMENT option.
#       - If the B_GROUP_END option is set, the current group is finalized and a new one is started.
#
#   Rule 2.:
#       - This rule forces alignment to the next byte boundary.
#       - The field is ignored during final class generation (name is discarded).
#       - The current group is finalized unless the bitfield is configured with B_GROUP_KEEP
#
#   Rule 3.:
#       - Equivalent to struct-like class field definitions.
#       - Automatically implies a rule 2 alignment.
#       - Always finalizes the current group regardless of B_GROUP_KEEP.
#
#   Rule 4.:
#       - Extension of Rule 1.
#       - Explicitly defines a conversion factory for the field.
#       - The factory must be:
#           - A built-in type (e.g., int, bool) supporting __int__, or
#           - A type or instance of BitfieldValueFactory.
#
#   Rule 5.:
#       - Builds upon Rule 4 with support for options.
#       - Options can be passed as a list or single element.
#       - Supported Options:
#           - NewGroup: Aligns the current group, starts a new one, and adds the entry to it.
#           - EndGroup: Adds the entry to the current group, then aligns it.
#           - SetAlignment: Changes the current working alignment.
#       - Note: Option order affects behavior and must be considered carefully.

#: The default alignment (in bits) used for bitfield group boundaries
DEFAULT_ALIGNMENT: int = 8

#: Alias for the `B_GROUP_NEW` flag, used to indicate that a new bitfield group should be started.
NewGroup: Final[Flag[None]] = B_GROUP_NEW

#: Alias for the `B_GROUP_END` flag, used to indicate that the current bitfield group
#: should be finalized.
EndGroup: Final[Flag[None]] = B_GROUP_END


class SetAlignment:
    """
    Instructional flag used to update the current bitfield alignment dynamically during
    bitfield generation.

    This class allows to explicitly set a new alignment boundary (in bits) for subsequent fields
    or groups in a bitfield definition. This enables finer control over how bitfield groups are
    organized and aligned.

    :param new_alignment: The alignment size in bits to be used from this point forward in the bitfield layout.
    :type new_alignment: int
    """

    def __init__(self, new_alignment: int) -> None:
        self.alignment: int = new_alignment

    @staticmethod
    def flag(new_alignment: int) -> Flag[int]:
        """Create a :class:`Flag` instance representing a request to set a new alignment.

        This method is intended for use where a generic :class:`Flag` is expected rather than a full
        :class:`SetAlignment` object, e.g. for setting options for a :class:`Field`.

        >>> field = 5 - uint32 | SetAlignment.flag(32)

        :param new_alignment: The alignment size in bits.
        :type new_alignment: int
        :return: A `Flag` object with the key `"bitfield.new_alignment"` and the specified alignment as its value.
        :rtype: Flag
        """
        return Flag("bitfield.new_alignment", new_alignment)

    @override
    def __hash__(self) -> int:
        return hash("SetAlignment")


def getbits(obj: object) -> int:
    """Retrieve the bit-width of a given object.

    This function checks for a :py:func:`__bits__` attribute on the object. The object must either implement
    the :class:`_SupportsBits` or :class:`_ContainsBits` protocol.

    >>> class A:
    ...     __bits__ = 3
    ...
    >>> a = A()
    >>> getbits(a)
    3

    :param obj: The object for which the bit-width should be determined. It is expected to have an :attr:`ATTR_BITS` attribute.
    :type obj: Any
    :return: The number of bits used by the object.
    :rtype: int
    :raises AttributeError: If the object does not have an attribute defined by :attr:`ATTR_BITS`.
    """
    # fmt: off
    __bits__: Callable[[], int] | int = getattr(obj, ATTR_BITS)  # pyright: ignore[reportAny]
    return __bits__() if callable(__bits__) else __bits__


def issigned(obj: object) -> bool:
    """Determine whether a given object represents a signed field.

    :param obj: The object for which signedness should be determined.
    :type obj: Any
    :return: :code:`True` if the field is marked as signed, :code:`False` otherwise.
    :rtype: bool
    """
    return bool(getattr(obj, ATTR_SIGNED, None))


_VT = TypeVar("_VT", default=int)


class BitfieldValueFactory(Generic[_VT]):
    """
    A generic factory class responsible for converting values between Python objects and integers
    for use in bitfield entries.

    By default, the factory converts to and from Python's built-in :code:`int` type, but it can be customized
    to support any type that accepts an integer in its constructor and implements :code:`__int__`.

    :param target:  The target type to which integer values will be converted., defaults to None
    :type target: type, optional
    """

    __slots__: tuple[str, ...] = ("target",)

    def __init__(self, target: Callable[[int], _VT] | None = None) -> None:
        self.target: Callable[[int], _VT] | type[int] = target or int

    def to_int(self, obj: _VT) -> int:
        """Convert a Python object to an integer.

        :param obj: The object to convert.
        :type obj: Any
        :return: The integer representation of the object.
        :rtype: int
        """
        return int(obj)  # pyright: ignore[reportArgumentType]

    def from_int(self, value: int):
        """Convert an integer to the target object type.

        :param value: The integer to convert.
        :type value: int
        :return: The value converted to the target type.
        :rtype: Any
        """
        return self.target(value)


_EnumT = TypeVar("_EnumT", bound=enum.Enum)


class EnumFactory(Generic[_EnumT], BitfieldValueFactory[_EnumT | int]):
    """A value factory for enum-like types used in bitfields.

    This factory attempts to convert between integers and enumeration instances,
    using the provided :code:`model` (which should support :code:`__int__`). It
    can operate in strict or lenient mode:

    - In strict mode, a :class:`ValueError` is raised if conversion fails.
    - In lenient mode, the raw integer is returned if the value is not in the enum.

    :param model: The enum model or mapping type to use.
    :type model: Type
    :param strict: Whether to raise an error on unknown values.
    :type strict: bool

    .. code-block:: python
        :caption: Example

        class Status(enum.IntEnum):
            OK = 0
            ERROR = 1

        factory = EnumFactory(Status, strict=True)
        factory.from_int(0)  # -> Status.OK
        factory.from_int(2)  # -> ValueError (strict mode)
    """

    def __init__(self, model: type[_EnumT], strict: bool = False) -> None:
        super().__init__(model)
        self.strict: bool = strict

    @override
    def from_int(self, value: int) -> int | _EnumT:
        """
        Convert an integer into an enum instance or raw int.

        :param value: The integer to convert.
        :type value: int
        :return: Enum instance or raw int if not found (in non-strict mode).
        :rtype: Any
        :raises ValueError: If strict is enabled and value is not valid.
        """
        try:
            return super().from_int(value)
        except ValueError:
            if self.strict:
                raise
            return value


class CharFactory(BitfieldValueFactory[str]):
    """
    A value factory for handling single ASCII/Unicode characters as integers.

    This factory allows treating a character field as a one-byte integer and vice versa,
    automatically converting during packing and unpacking.
    """

    def __init__(self) -> None:
        super().__init__(str)

    @override
    def from_int(self, value: int) -> str:
        """
        Convert an integer to its character representation.

        :param value: Integer ASCII or Unicode code point.
        :type value: int
        :return: Corresponding character.
        :rtype: str
        """
        return chr(value)

    @override
    def to_int(self, obj: str) -> int:
        """
        Convert a character to its integer (ordinal) representation.

        :param obj: The character to convert.
        :type obj: str
        :return: Corresponding integer value.
        :rtype: int
        """
        return ord(obj)


class BitfieldEntry:
    """
    Represents a single entry in a bitfield, including its bit position, width, name, and
    conversion behavior.

    May also represent a special action or directive instead of a field.

    :param bit: The starting bit position within its group.
    :type bit: int
    :param width: The number of bits used by this field.
    :type width: int
    :param name: The name of the field.
    :type name: str
    :param factory: A factory for type conversion. Defaults to BitfieldValueFactory.
    :type factory: type or BitfieldValueFactory or None
    :param action: Optional action object for special handling (e.g., alignment or padding).
    :type action: Any
    """

    __slots__: tuple[str, ...] = (
        "bit",
        "width",
        "name",
        "factory",
        "action",
        "low_mask",
    )

    def __init__(
        self,
        bit: int,
        width: int,
        name: str,
        factory: BitfieldValueFactory | type[BitfieldValueFactory] | None = None,
        action: _ActionLike | None = None,
    ) -> None:
        # fmt: off
        self.bit: int = bit
        self.width: int = width
        self.name: str = name
        factory = factory or BitfieldValueFactory()
        if isinstance(factory, type):
            self.factory: BitfieldValueFactory = self.factory()  # pyright: ignore[reportCallIssue]
        else:
            self.factory = factory
        self.action: _ActionLike | None = action
        self.low_mask: int = (1 << self.width) - 1

    @staticmethod
    def new_action(action: _ActionLike) -> "BitfieldEntry":
        """
        Create a new action-type entry (e.g., padding, control directive).

        :param action: The action object to encapsulate.
        :type action: Any
        :return: A BitfieldEntry instance with no bit-width, used for meta instructions.
        :rtype: BitfieldEntry
        """
        return BitfieldEntry(0, 0, "<action>", action=action)

    def shift(self, value_width: int) -> int:
        """
        Calculate how much to shift the field when extracting it from a value.

        :param value_width: The total bit width of the container.
        :type value_width: int
        :return: The number of bits to shift.
        :rtype: int
        """
        bit_pos = max(0, value_width - self.bit)
        return max(bit_pos - self.width, 0)

    def is_action(self) -> bool:
        """
        Check whether this entry is an action (i.e., not a data field).

        :return: True if this is an action entry.
        :rtype: bool
        """
        return self.action is not None

    @override
    def __repr__(self) -> str:
        """
        Return a human-readable string representation of the bitfield entry.

        :return: String representation.
        :rtype: str
        """
        if self.is_action():
            return repr(self.action)

        r = f"<Entry {self.name!r}: bit={self.bit}, width={self.width}"
        if self.factory:
            type_ = type(self.factory)
            if type_ is BitfieldValueFactory:
                type_ = self.factory.target

            r = f"{r}, factory={type_.__name__}"
        return f"{r}>"


class BitfieldGroup:
    """
    A group of one or more bitfield entries. Groups are used to organize fields within a single
    alignment unit and may represent either packed fields or standalone fields.

    :param bit_count: The number of bits in the group, or -1 for single field representation.
    :type bit_count: int
    """

    __slots__: tuple[str, ...] = ("entries", "bit_count")

    def __init__(self, bit_count: int) -> None:
        self.bit_count: int = bit_count
        self.entries: list[BitfieldEntry] = []

    def is_field(self) -> bool:
        """
        Determine whether the group contains a single non-bitfield field.

        :return: True if the group holds a single struct-like field.
        :rtype: bool
        """
        return self.bit_count == -1

    def get_field(self) -> Field:
        """
        Get the single field from this group.

        :return: The field object.
        :rtype: BitfieldEntry
        """
        return self.entries[0]  # pyright: ignore[reportReturnType]

    def set_field(self, field: BitfieldEntry | Field):
        """
        Set the group to hold only the given field and mark it as a standalone field group.

        :param field: The field to store in this group.
        :type field: BitfieldEntry
        """
        self.entries = [field]  # pyright: ignore[reportAttributeAccessIssue]
        self.bit_count = -1

    def align_to(self, alignment: int):
        """
        Align the bit count of this group to the specified boundary.

        :param alignment: The number of bits to align to.
        :type alignment: int
        """
        if not self.is_field():
            pad = self.bit_count % alignment
            if pad > 0:
                self.bit_count += alignment - pad

    def is_empty(self) -> bool:
        """
        Check if the group contains any entries.

        :return: True if the group is empty.
        :rtype: bool
        """
        return len(self.entries) == 0

    def get_size(self, context: _ContextLike | None = None) -> int:
        """
        Get the size of this group in bytes.

        :param context: Optional context used for size evaluation.
        :type context: Any
        :return: The size of the group in bytes.
        :rtype: int
        """
        if self.is_field():
            field = self.get_field()
            return field.__size__(context) if context else sizeof(field)

        return self.bit_count // 8

    def get_bits(self, context: _ContextLike | None = None):
        """
        Get the total number of bits in this group.

        :param context: Optional context used for size evaluation.
        :type context: Any
        :return: The number of bits.
        :rtype: int
        """
        return self.get_size(context) * 8

    @override
    def __repr__(self) -> str:
        if self.is_field():
            return repr(self.get_field())

        return f"<BitfieldGroup ({self.bit_count}) {self.entries!r}>"


class Bitfield(Struct[_VT]):
    """
    A Bitfield represents a packed structure composed of bit-level fields. This
    class allows for the declarative definition of compact memory representations
    where each field can occupy an arbitrary number of bits, not necessarily
    aligned to byte boundaries.

    Core Implementation:
    - Bitfields are organized into BitfieldGroups, which manage alignment and field aggregation.
    - Entries can be individual bit widths or wrapped fields with explicit alignment.
    - Special field options like NewGroup and EndGroup can control group layout.
    - Supports value factories for type conversion and symbolic runtime actions.

    Available global options:
    - :code:`B_NO_AUTO_BOOL`: disables automatically converting 1bit fields to boolean
    - :code:`B_GROUP_KEEP`: disables finalizing groups when using the alignment definition syntax

    :param model: The model for the structure.
    :type model: Any
    :param order: Byte order of the structure.
    :type order: Optional[str]
    :param arch: Target architecture.
    :type arch: Optional[str]
    :param options: Global structure options.
    :type options: Optional[set]
    :param field_options: Field-specific options.
    :type field_options: Optional[set]
    :param alignment: Bit alignment size.
    :type alignment: Optional[int]
    """

    __slots__: tuple[str, ...] = (
        "groups",
        "alignment",
    )

    def __init__(
        self,
        model: type[_VT],
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        alignment: int | None = None,
    ) -> None:
        self.alignment: int = alignment or DEFAULT_ALIGNMENT
        # These fields remain private and will be deleted after processing
        self._current_alignment: int = self.alignment
        self._current_group: BitfieldGroup = BitfieldGroup(self._current_alignment)
        self._bit_pos: int = 0
        self.groups: list[BitfieldGroup] = [self._current_group]
        super().__init__(
            model=model,
            order=order,
            arch=arch,
            options=options,
            field_options=field_options,
        )
        # Add additional options based on the struct's type
        self.options.difference_update(GLOBAL_STRUCT_OPTIONS, GLOBAL_UNION_OPTIONS)
        self.options.update(GLOBAL_BITFIELD_FLAGS)

        self.groups = [group for group in self.groups if not group.is_empty()]
        self.groups[-1].align_to(self._current_alignment)
        # REVISIT: should be enable modification after processing?
        del self._bit_pos
        del self._current_alignment
        del self._current_group

    @override
    def __add__(self, sequence: Sequence[Any, Any, Any]) -> Self:
        """
        Append another Bitfield instance to this one.

        :param sequence: Another Bitfield instance.
        :type sequence: Bitfield
        :return: Combined Bitfield.
        :rtype: Bitfield
        :raises TypeError: If sequence is not a Bitfield.
        """
        if not isinstance(sequence, Bitfield):
            # REVISIT: we could just add each field as a group individually?
            raise TypeError(
                f"Attempted to add a non-bitfield struct to a bitfield! (type={type(sequence)})"
            )

        self.groups.extend(sequence.groups)
        return super(Struct, self).__add__(sequence)

    def _process_align(
        self, options: list[_OptionLike[Any] | SetAlignment] | None
    ) -> Field:
        """
        Process an alignment directive.

        .. code-block:: bnf

            <name> : 0

        :param options: A list of alignment-related options.
        :type options: Optional[list]
        :return: A placeholder field.
        :rtype: Field
        """
        # 2.: the current group will be finalized
        self._current_group.align_to(self._current_alignment)
        if not self.has_option(B_GROUP_KEEP):
            self._current_group = self._new_group(self._current_alignment)
        else:
            self._bit_pos = self._current_group.bit_count

        for option in options or []:
            if not self._process_alignment_option(option):
                alignment = self._current_alignment
                group = self._current_group
                if option.name in (EndGroup.name, NewGroup.name):
                    # finalize current group (same effect for alignment statement)
                    group.align_to(alignment)
                    self._current_group = self._new_group(alignment)

        return Field(Pass)

    def _process_bits(
        self,
        name: str,
        bits: int,
        factory: (
            BitfieldValueFactory[Any] | type[BitfieldValueFactory[Any]] | None
        ) = None,
        options: list[_OptionLike[Any] | SetAlignment] | None = None,
    ) -> Field:
        """
        Process a bitfield entry with a given width.

        :param name: Field name.
        :type name: str
        :param bits: Width in bits.
        :type bits: int
        :param factory: Optional value factory.
        :type factory: Optional[BitfieldValueFactory]
        :param options: Field-specific options.
        :type options: Optional[list]
        :return: Resulting Field.
        :rtype: Field
        """
        if bits == 0:
            return self._process_align(options)

        if not factory and bits == 1 and not self.has_option(B_NO_AUTO_BOOL):
            factory = BitfieldValueFactory(bool)

        entry = BitfieldEntry(self._bit_pos, bits, name, factory)
        if not self._process_options(options, entry):
            group = self._current_group
            group.entries.append(entry)
            # Adjust the size of the goup dynamically
            self._bit_pos += entry.width
            group.bit_count = max(group.bit_count, self._bit_pos)
        # this is only symbolic
        return Field(Int(bits))

    def _process_bits_field(
        self,
        name: str,
        field: Field,
        options: list[_OptionLike[Any] | SetAlignment] | None = None,
        factory: (
            BitfieldValueFactory[Any] | type[BitfieldValueFactory[Any]] | None
        ) = None,
    ) -> Field:
        """
        Process a bitfield that wraps another field instance.

        :param name: Field name.
        :type name: str
        :param field: The field instance.
        :type field: Field
        :param options: List of options.
        :type options: Optional[list]
        :param factory: Optional value factory.
        :type factory: Optional[BitfieldValueFactory]
        :return: Resulting Field.
        :rtype: Field
        :raises TypeError: If bit width is not an integer.
        """
        if field.bits is None:
            # we don't need to check for NewGroup and EndGroup options here as no
            # bits are specified and the field gets its own group.
            for option in options or []:
                self._process_alignment_option(
                    option
                )  # pyright: ignore[reportUnusedCallResult]

            # bits not present -> treat defintion as simple field, which means we finalize
            # the current group, create a new FIELD GROUP and another new one after that
            self._current_group.align_to(self._current_alignment)
            field_group = self._new_group(-1)
            field_group.set_field(field)
            self._current_group = self._new_group(self._current_alignment)
            return field

        width = field.bits
        if not isinstance(width, int):
            raise TypeError(
                f"Bitfield: field definition of {name!r} requires an integer as bits"
            )

        entry = BitfieldEntry(
            self._bit_pos, width, name, factory or BitfieldValueFactory(typeof(field))
        )
        if not self._process_options(options, entry):
            group = self._current_group
            group.entries.append(entry)
            self._bit_pos += width
            group.bit_count = max(group.bit_count, self._bit_pos)

        if field.has_flag(B_OVERWRITE_ALIGNMENT):
            try:
                field_bits = getbits(field.struct)
            except Exception:
                field_bits = sizeof(field) * 8

            self._current_alignment = field_bits or DEFAULT_ALIGNMENT
            self._current_group.align_to(self._current_alignment)

        return field

    def _process_options(
        self,
        options: list[_OptionLike[Any] | SetAlignment] | None,
        entry: BitfieldEntry | None = None,
    ) -> bool:
        # fmt: off
        consumed = False
        for option in options or []:
            if self._process_alignment_option(option):
                continue

            group = self._current_group
            alignment = self._current_alignment
            if option.name == EndGroup.name:  # pyright: ignore[reportAttributeAccessIssue]
                if entry:
                    group.entries.append(entry)
                    self._bit_pos += entry.width
                    group.bit_count = max(group.bit_count, self._bit_pos)
                    consumed = True

                group.align_to(alignment)
                self._current_group = self._new_group(alignment)
            elif option.name == NewGroup.name:  # pyright: ignore[reportAttributeAccessIssue]
                # finalize current group, create a new one and add the entry to the newly
                # created group
                group.align_to(alignment)
                self._current_group = group = self._new_group(alignment)

                if entry:
                    group.entries.append(entry)
                    # position was reset to zero
                    self._bit_pos += entry.width
                    group.bit_count = max(group.bit_count, self._bit_pos)
                    consumed = True
        return consumed

    def _new_group(self, alignment: int) -> BitfieldGroup:
        new_group = BitfieldGroup(alignment)
        self.groups.append(new_group)
        self._bit_pos = 0
        return new_group

    @overload
    def _process_alignment_option(self, option: SetAlignment) -> Literal[True]: ...
    @overload
    def _process_alignment_option(self, option: _OptionLike[Any]) -> Literal[False]: ...
    def _process_alignment_option(
        self, option: SetAlignment | _OptionLike[Any]
    ) -> bool:
        if isinstance(option, SetAlignment):
            # update current working alignment
            self._current_alignment = option.alignment or DEFAULT_ALIGNMENT
            self._current_group.align_to(self._current_alignment)
            return True
        elif isinstance(option, Flag):
            if option.name == "bitfield.new_alignment":
                self._current_alignment = option.value or DEFAULT_ALIGNMENT
                self._current_group.align_to(self._current_alignment)
                return True

        return False

    @override
    def _process_field(
        self, name: str, annotation: _AnnotationT, default: Any
    ) -> Field:
        arch: _ArchLike | None = self.arch
        order: _EndianLike | None = (
            self.order
        )  # getattr(annotation, ATTR_BYTEORDER, None)
        match annotation:
            case int():
                if annotation == 0:
                    return self._process_align(None)
                else:
                    # 1. (without field) defines the width using the default value factory
                    return self._process_bits(name, annotation)

            case tuple():  # NEW EXTENDED DEFINITION
                if len(annotation) == 0:
                    raise ValueError(
                        f"Extended field definition for {name!r} does not define any values!"
                    )

                if len(annotation) == 1:
                    # definition: (<bits>, )
                    (width,) = annotation
                    if width == 0:
                        raise ValueError(
                            f"Extended field {name!r} defines forbidden width of zero"
                        )

                    return self._process_bits(name, width)

                options = []
                factory = None
                (width, factory_or_option, *extra_options) = annotation
                if isinstance(factory_or_option, BitfieldValueFactory):
                    factory = factory_or_option
                elif isinstance(factory_or_option, type):
                    # here we enable just specifying types instead of a factory
                    if not issubclass(factory_or_option, BitfieldValueFactory):
                        factory = BitfieldValueFactory(factory_or_option)
                    else:
                        factory = factory_or_option()
                else:
                    # treat as option or as a list of options
                    options = (
                        [factory_or_option]
                        if not isinstance(factory_or_option, Iterable)
                        else list(factory_or_option)
                    )

                # extra options may be a list or single element
                for extra in extra_options:
                    options.extend(extra if isinstance(extra, Iterable) else [extra])

                if isinstance(width, int):
                    # rule no. 5
                    return self._process_bits(name, width, factory, options)

                field: _StructLike = width
                if not isinstance(field, Field):
                    field = Field(field, order=order, arch=arch, default=default)
                else:
                    if not field.has_order():
                        field.order = order
                    if not field.has_arch():
                        field.arch = arch
                return self._process_bits_field(name, field, options, factory)

            case _:
                # rule 1 (with field) or rule 3
                field = self._process_annotation(annotation, default, order, arch)
                if not isinstance(field, Field):
                    field = Field(field, order=order, arch=arch, default=default)
                else:
                    if not field.has_order():
                        field.order = order
                    if not field.has_arch():
                        field.arch = arch
                return self._process_bits_field(name, field)

    @override
    def _included(self, name: str, default: Any, annotation: Any) -> bool:
        if not super()._included(name, default, annotation):
            return False

        width = annotation
        if isinstance(annotation, tuple):
            width, *_ = annotation

        if isinstance(width, int):
            return width != 0

        if isinstance(width, Field):
            return width.bits != 0
        return True

    @override
    def _replace_type(self, name: str, type_: type) -> None:
        entry = self.get_entry(name)
        if entry is not None:
            if not entry.factory:
                type_ = int
            elif isinstance(entry.factory, BitfieldValueFactory):
                # REVISIT: what if .target is a function?
                type_ = entry.factory.target or object
            else:
                type_ = object

        # else: must be a field with a known type
        return super()._replace_type(name, type_)

    @override
    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the total size of the bitfield structure.

        :param context: Packing context.
        :type context: Any
        :return: Total size in bytes.
        :rtype: int
        """
        # size is different as our model includes correct padding
        return sum(map(lambda g: g.get_size(context), self.groups))

    def __bits__(self) -> int:
        """
        Compute the total number of bits in the structure.

        :return: Total bit count.
        :rtype: int
        """
        return sum(map(lambda g: g.get_bits(), self.groups))

    @override
    def unpack_one(self, context: _ContextLike) -> _VT:
        init_data = (O_CONTEXT_FACTORY.value or Context)()
        context[CTX_OBJECT] = (O_CONTEXT_FACTORY.value or Context)(_parent=context)

        field: Field | None = context.get(CTX_FIELD)
        base_path: str = context[CTX_PATH]
        # REVISIT
        order: _EndianLike = (
            field.order
            if field
            else (self.order or O_DEFAULT_ENDIAN.value or LittleEndian)
        )
        endian = "little" if order.ch == LITTLE_ENDIAN_FMT else "big"
        for group in self.groups:
            if group.is_field():
                # unpack using field instance
                field = group.get_field()
                name = field.__name__
                context[CTX_PATH] = f"{base_path}.{name}"
                value = field.__unpack__(context)
                context[CTX_OBJECT][name] = value
                if name in self._members:
                    init_data[name] = value

            else:
                raw_data = context[CTX_STREAM].read(group.get_size())
                if not raw_data:
                    # set context path to next entry for debugging
                    context[CTX_PATH] = f"{base_path}.{group.entries[0].name}"
                    raise StructException(
                        f"Failed to parse group of size {group.bit_count}bits: unexpected EOF!",
                        context,
                    )
                raw_value = int.from_bytes(raw_data, endian)
                for entry in group.entries:
                    # each entry may be an action
                    context[CTX_PATH] = f"{base_path}.{entry.name}"
                    if entry.is_action():
                        func = getattr(entry.action, ATTR_ACTION_UNPACK, None)
                        if func:
                            func(context)
                            continue

                    if entry.name not in self._members:
                        continue

                    value = (raw_value >> entry.shift(group.bit_count)) & entry.low_mask
                    if entry.factory:
                        value = entry.factory.from_int(value)

                    init_data[entry.name] = value

        return self.model(**init_data)  # pyright: ignore[reportCallIssue]

    @override
    def pack_one(self, obj: _VT, context: _ContextLike) -> None:
        base_path = context[CTX_PATH]
        field: Field | None = context.get(CTX_FIELD)
        # REVISIT
        order: _EndianLike = (
            field.order
            if field
            else (self.order or O_DEFAULT_ENDIAN.value or LittleEndian)
        )
        endian = "little" if order.ch == LITTLE_ENDIAN_FMT else "big"
        for group in self.groups:
            if group.is_field():
                field = group.get_field()
                name = field.get_name()
                context[CTX_PATH] = f"{base_path}.{name}"
                if name in self._members:
                    value = self.get_value(obj, name, field)
                else:
                    value = field.default if field.default != INVALID_DEFAULT else None

                field.__pack__(value, context)
            else:
                value = 0
                for entry in group.entries:
                    context[CTX_PATH] = f"{base_path}.{entry.name}"
                    if entry.is_action():
                        func = getattr(entry.action, ATTR_ACTION_PACK, None)
                        if func:
                            func(context)
                        continue

                    if entry.name not in self._members:
                        continue

                    entry_value = self.get_value(obj, entry.name, None)
                    if entry.factory:
                        entry_value = entry.factory.to_int(entry_value)

                    # silently ignore invalid values
                    value |= (entry_value & entry.low_mask) << entry.shift(
                        group.bit_count
                    )
                context[CTX_STREAM].write(value.to_bytes(group.bit_count // 8, endian))

    @override
    def add_action(self, action: _ActionLike) -> None:
        self._current_group.entries.append(
            BitfieldEntry(0, 0, "<action>", action=action)
        )
        return super().add_action(action)

    def get_entry(self, name: str) -> BitfieldEntry | None:
        # fmt: off
        for group in self.groups:
            if group.is_field():
                continue

            for entry in group.entries:
                if entry.name == name:
                    return entry


class BitfieldDefMixin(StructDefMixin):
    """Mixin extending :class:`StructDefMixin` for ``Bitfield``-based models.

    This mixin behaves identically to :class:`StructDefMixin` but binds the
    ``__struct__`` attribute to a :class:`Bitfield` definition instead of a
    regular :class:`Struct`. It allows bitfield models to reuse the same
    convenience API (``from_bytes``, ``to_bytes``, ``[]`` operator, etc.)
    while operating on compact bit-level layouts.
    """

    # fmt: off
    __struct__: ClassVar[Bitfield[Self]]  # pyright: ignore[reportIncompatibleVariableOverride]
    """Reference to the bitfield model"""

class bitfield_factory:
    """Factory for transforming plain classes into ``Bitfield`` models.

    This factory mirrors the behavior of :class:`struct_factory` but targets
    bit-level structures. It allows developers to declare compact bitfield
    layouts using class syntax while retaining full type-checker awareness
    through ``@dataclass_transform``.
    """

    mixin: type[BitfieldDefMixin] = BitfieldDefMixin

    @dataclass_transform(field_specifiers=(dataclasses.field, Invisible))
    @staticmethod
    def make_bitfield(
        ty: type[_VT],
        /,
        *,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        alignment: int | None = None,
    ) -> type:
        """Create a ``Bitfield`` model from a class definition.

        This helper performs the underlying transformation by constructing
        a :class:`Bitfield` instance and returning the generated model class.

        :param ty: The base class to transform into a Bitfield model
        :type ty: type[_VT]
        :param order: Byte order used during serialization, defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Architecture configuration inferred by fields,
            defaults to None
        :type arch: _ArchLike | None, optional
        :param options: Additional options controlling bitfield behavior,
            defaults to None
        :type options: Iterable[_OptionLike] | None, optional
        :param field_options: Default options applied to bitfield members,
            defaults to None
        :type field_options: Iterable[_OptionLike] | None, optional
        :param alignment: Optional bit alignment constraint, defaults to None
        :type alignment: int | None, optional
        :return: The generated Bitfield model class
        :rtype: type
        """
        b = Bitfield(
            ty,
            order=order,
            arch=arch,
            options=options,
            field_options=field_options,
            alignment=alignment,
        )
        return b.model

    @overload
    @dataclass_transform(
        kw_only_default=True, field_specifiers=(dataclasses.field, Invisible)
    )
    @staticmethod
    def bitfield(
        ty: type[_VT],
        /,
        *,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        alignment: int | None = None,
    ) -> type[_VT]: ...
    @overload
    @dataclass_transform(
        kw_only_default=True, field_specifiers=(dataclasses.field, Invisible)
    )
    @staticmethod
    def bitfield(
        ty: None = None,
        /,
        *,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        alignment: int | None = None,
    ) -> Callable[[type[_VT]], type[_VT]]: ...
    @dataclass_transform(
        kw_only_default=True, field_specifiers=(dataclasses.field, Invisible)
    )
    @staticmethod
    def bitfield(
        ty: type[_VT] | None = None,
        /,
        *,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        alignment: int | None = None,
    ) -> type[_VT] | Callable[[type[_VT]], type[_VT]]:
        """Decorator or direct transformer for creating a ``Bitfield`` model.

        This method can be used either as:

        - A decorator: ``@bitfield(...)``
        - A direct transformer: ``MyBitfield = bitfield(MyClass, ...)``

        It enables defining compact bit-level layouts using standard class
        syntax while preserving dataclass semantics and static type checking.

        >>> from caterpillar.py import bitfield, SetAlignment, uint16
        >>> @bitfield
        ... class Packet:
        ...     version   : 3
        ...     type      : (5, SetAlignment(16))
        ...     length    : 10
        ...     _         : 0  # align to 16bits
        ...     payload   : uint16
        ...
        >>> # You can now pack/unpack Packet instances as compact binary bitfields
        >>> pkt = Packet(version=1, type=2, length=128, payload=0xABCD)
        >>> packed = pack(pkt)
        >>> unpacked = unpack(Packet, packed)

        :param ty: The user-defined class to transform. If None, a decorator
            function is returned
        :type ty: type[_VT] | None, optional
        :param order: Byte order used during serialization, defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Architecture configuration inferred by fields,
            defaults to None
        :type arch: _ArchLike | None, optional
        :param options: Additional options controlling bitfield behavior,
            defaults to None
        :type options: Iterable[_OptionLike] | None, optional
        :param field_options: Default options applied to bitfield members,
            defaults to None
        :type field_options: Iterable[_OptionLike] | None, optional
        :param alignment: Optional bit alignment constraint, defaults to None
        :type alignment: int | None, optional
        :return: The decorated Bitfield model class or a decorator function
        :rtype: type[_VT] | Callable[[type[_VT]], type[_VT]]
        """

        def wrap(cls: type[_VT]) -> type[_VT]:
            return bitfield_factory.make_bitfield(
                cls,
                options=options,
                order=order,
                arch=arch,
                field_options=field_options,
                alignment=alignment,
            )

        if ty is not None:
            return bitfield_factory.make_bitfield(
                ty,
                options=options,
                order=order,
                arch=arch,
                field_options=field_options,
                alignment=alignment,
            )

        return wrap


bitfield = bitfield_factory.bitfield
