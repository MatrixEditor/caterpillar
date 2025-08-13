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
from collections.abc import Iterable
from caterpillar.fields.common import Int
from caterpillar.shared import (
    ATTR_ACTION_PACK,
    ATTR_ACTION_UNPACK,
    ATTR_BYTEORDER,
    typeof,
    ATTR_BITS,
    ATTR_SIGNED,
)
from caterpillar.byteorder import (
    LittleEndian,
    SysNative,
    system_arch,
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
from caterpillar.context import CTX_PATH, O_CONTEXT_FACTORY, CTX_OBJECT, CTX_STREAM

from ._struct import Struct, sizeof


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
DEFAULT_ALIGNMENT = 8

#: Alias for the `B_GROUP_NEW` flag, used to indicate that a new bitfield group should be started.
NewGroup = B_GROUP_NEW

#: Alias for the `B_GROUP_END` flag, used to indicate that the current bitfield group
#: should be finalized.
EndGroup = B_GROUP_END


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
        self.alignment = new_alignment

    @staticmethod
    def flag(new_alignment: int):
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

    def __hash__(self) -> int:
        return hash("SetAlignment")


def getbits(obj) -> int:
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
    __bits__ = getattr(obj, ATTR_BITS)
    return __bits__() if callable(__bits__) else __bits__


def issigned(obj) -> bool:
    """Determine whether a given object represents a signed field.

    :param obj: The object for which signedness should be determined.
    :type obj: Any
    :return: :code:`True` if the field is marked as signed, :code:`False` otherwise.
    :rtype: bool
    """
    return bool(getattr(obj, ATTR_SIGNED, None))


class BitfieldValueFactory:
    """
    A generic factory class responsible for converting values between Python objects and integers
    for use in bitfield entries.

    By default, the factory converts to and from Python's built-in :code:`int` type, but it can be customized
    to support any type that accepts an integer in its constructor and implements :code:`__int__`.

    :param target:  The target type to which integer values will be converted., defaults to None
    :type target: type, optional
    """

    __slots__ = ("target",)

    def __init__(self, target=None) -> None:
        self.target = target or int

    def to_int(self, obj) -> int:
        """Convert a Python object to an integer.

        :param obj: The object to convert.
        :type obj: Any
        :return: The integer representation of the object.
        :rtype: int
        """
        return int(obj)

    def from_int(self, value: int):
        """Convert an integer to the target object type.

        :param value: The integer to convert.
        :type value: int
        :return: The value converted to the target type.
        :rtype: Any
        """
        return self.target(value)


class EnumFactory(BitfieldValueFactory):
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

    def __init__(self, model, strict=False) -> None:
        super().__init__(model)
        self.strict = strict

    def from_int(self, value: int):
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


class CharFactory(BitfieldValueFactory):
    """
    A value factory for handling single ASCII/Unicode characters as integers.

    This factory allows treating a character field as a one-byte integer and vice versa,
    automatically converting during packing and unpacking.
    """

    def __init__(self) -> None:
        super().__init__(str)

    def from_int(self, value: int):
        """
        Convert an integer to its character representation.

        :param value: Integer ASCII or Unicode code point.
        :type value: int
        :return: Corresponding character.
        :rtype: str
        """
        return chr(value)

    def to_int(self, obj) -> int:
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

    __slots__ = ("bit", "width", "name", "factory", "action", "low_mask")

    def __init__(
        self, bit: int, width: int, name: str, factory=None, action=None
    ) -> None:
        self.bit = bit
        self.width = width
        self.name = name
        self.factory = factory or BitfieldValueFactory()
        if isinstance(self.factory, type):
            self.factory = self.factory()
        self.action = action
        self.low_mask = (1 << self.width) - 1

    @staticmethod
    def new_action(action):
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

    __slots__ = ("entries", "bit_count")

    def __init__(self, bit_count: int) -> None:
        self.bit_count = bit_count
        self.entries = []

    def is_field(self) -> bool:
        """
        Determine whether the group contains a single non-bitfield field.

        :return: True if the group holds a single struct-like field.
        :rtype: bool
        """
        return self.bit_count == -1

    def get_field(self):
        """
        Get the single field from this group.

        :return: The field object.
        :rtype: BitfieldEntry
        """
        return self.entries[0]

    def set_field(self, field):
        """
        Set the group to hold only the given field and mark it as a standalone field group.

        :param field: The field to store in this group.
        :type field: BitfieldEntry
        """
        self.entries = [field]
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

    def get_size(self, context=None):
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

    def get_bits(self, context=None):
        """
        Get the total number of bits in this group.

        :param context: Optional context used for size evaluation.
        :type context: Any
        :return: The number of bits.
        :rtype: int
        """
        return self.get_size(context) * 8

    def __repr__(self) -> str:
        if self.is_field():
            return repr(self.get_field())

        return f"<BitfieldGroup ({self.bit_count}) {self.entries!r}>"


class Bitfield(Struct):
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

    __slots__ = (
        "groups",
        "alignment",
    )

    def __init__(
        self,
        model,
        order=None,
        arch=None,
        options=None,
        field_options=None,
        alignment=None,
    ) -> None:
        self.alignment = alignment or DEFAULT_ALIGNMENT
        # These fields remain private and will be deleted after processing
        self._current_alignment = self.alignment
        self._current_group = BitfieldGroup(self._current_alignment)
        self._bit_pos = 0
        self.groups = [self._current_group]
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

    def __add__(self, sequence):
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

    def _process_align(self, options) -> Field:
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
            if self._process_alignment_option(option):
                continue

            alignment = self._current_alignment
            group = self._current_group
            if option.name in (EndGroup.name, NewGroup.name):
                # finalize current group (same effect for alignment statement)
                group.align_to(alignment)
                self._current_group = self._new_group(alignment)

        return Field(Pass)

    def _process_bits(self, name: str, bits: int, factory=None, options=None) -> Field:
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
        self, name: str, field, options=None, factory=None
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
                self._process_alignment_option(option)

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

    def _process_options(self, options, entry=None) -> bool:
        consumed = False
        for option in options or []:
            if self._process_alignment_option(option):
                continue

            group = self._current_group
            alignment = self._current_alignment
            if option.name == EndGroup.name:
                if entry:
                    group.entries.append(entry)
                    self._bit_pos += entry.width
                    group.bit_count = max(group.bit_count, self._bit_pos)
                    consumed = True

                group.align_to(alignment)
                self._current_group = self._new_group(alignment)
            elif option.name == NewGroup.name:
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

    def _new_group(self, alignment):
        new_group = BitfieldGroup(alignment)
        self.groups.append(new_group)
        self._bit_pos = 0
        return new_group

    def _process_alignment_option(self, option):
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

    def _process_field(self, name: str, annotation, default):
        arch = self.arch or system_arch
        order = getattr(annotation, ATTR_BYTEORDER, self.order or SysNative)
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

                field = width
                if not isinstance(field, Field):
                    field = Field(field, order=order, arch=arch, default=default)

                return self._process_bits_field(name, field, options, factory)

            case _:
                # rule 1 (with field) or rule 3
                field = self._process_annotation(annotation, default, order, arch)
                if not isinstance(field, Field):
                    field = Field(field, order=order, arch=arch, default=default)
                return self._process_bits_field(name, field)

    def _included(self, name: str, default, annotation) -> bool:
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

    def _replace_type(self, name: str, type_: type) -> None:
        entry = self.get_entry(name)
        if entry is not None:
            if not entry.factory:
                type_ = int
            elif isinstance(entry.factory, BitfieldValueFactory):
                type_ = entry.factory.target or object
            else:
                type_ = object

        # else: must be a field with a known type
        return super()._replace_type(name, type_)

    def __size__(self, context) -> int:
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

    def unpack_one(self, context):
        init_data = O_CONTEXT_FACTORY.value()
        context[CTX_OBJECT] = O_CONTEXT_FACTORY.value(_parent=context)
        base_path = context[CTX_PATH]
        # REVISIT
        endian = "little" if self.order == LittleEndian else "big"
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

        return self.model(**init_data)

    def pack_one(self, obj, context) -> None:
        base_path = context[CTX_PATH]
        # REVISIT
        endian = "little" if self.order == LittleEndian else "big"
        for group in self.groups:
            if group.is_field():
                field = group.get_field()
                name = field.__name__
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

    def add_action(self, action) -> None:
        self._current_group.entries.append(
            BitfieldEntry(0, 0, "<action>", action=action)
        )
        return super().add_action(action)

    def get_entry(self, name: str):
        for group in self.groups:
            if group.is_field():
                continue

            for entry in group.entries:
                if entry.name == name:
                    return entry


def _make_bitfield(
    cls: type,
    /,
    *,
    options,
    order=None,
    arch=None,
    field_options=None,
    alignment=None,
) -> type:
    _ = Bitfield(
        cls,
        order=order,
        arch=arch,
        options=options,
        field_options=field_options,
        alignment=alignment,
    )
    return cls


def bitfield(
    cls=None,
    /,
    *,
    options=None,
    order=None,
    arch=None,
    field_options=None,
    alignment=None,
):
    """
    Decorator that transforms a class definition into a :class:`Bitfield` structure.

    This decorator enables defining bitfields using simple class syntax,
    with support for custom alignment, ordering, architecture, and field options.

    :param cls: The user-defined class to transform.
    :type cls: Optional[type]
    :param options: A set of global or structure-specific options.
    :type options: Optional[set]
    :param order: Optional byte order for serialization (e.g., 'little' or 'big').
    :type order: Optional[str]
    :param arch: Optional architecture string (e.g., 'x86', 'arm').
    :type arch: Optional[str]
    :param field_options: Optional default options for fields.
    :type field_options: Optional[set]
    :param alignment: Optional alignment in bits.
    :type alignment: Optional[int]
    :return: The decorated class, enhanced as a `Bitfield` structure.
    :rtype: type

    .. code-block:: python

        from caterpillar.py import bitfield, SetAlignment, uint16

        @bitfield
        class Packet:
            version   : 3
            type      : (5, SetAlignment(16))
            length    : 10
            _         : 0  # align to 16bits
            payload   : uint16

        # You can now pack/unpack Packet instances as compact binary bitfields
        pkt = Packet(version=1, type=2, length=128, payload=0xABCD)
        packed = pack(pkt)
        unpacked = unpack(Packet, packed)
    """

    def wrap(cls):
        return _make_bitfield(
            cls,
            options=options,
            order=order,
            arch=arch,
            field_options=field_options,
            alignment=alignment,
        )

    if cls is not None:
        return _make_bitfield(
            cls,
            options=options,
            order=order,
            arch=arch,
            field_options=field_options,
            alignment=alignment,
        )

    return wrap
