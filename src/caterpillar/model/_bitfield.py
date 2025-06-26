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
    Flag,
)
from caterpillar.fields import (
    Field,
    Pass,
    INVALID_DEFAULT,
)
from caterpillar.exception import StructException
from caterpillar.context import CTX_PATH, Context, CTX_OBJECT, CTX_STREAM

from ._struct import Struct, sizeof


# --- BItfield Concept ---
# NEW REVISED CONCEPT
# Each Bitfield stores a sequence of so-called bitfield-groups, whereby each group stores
# a collection of sized fields. A bitfield-group may be represented by a collection of other
# fields (_StructLike) or a single _StructLike object. For instance, consider the following
# bitfield definition:
#
#   @bitfield
#   class Format:
#       a1: 1
#       a2: 1 - boolean
#       _ : 0
#       b1: char
#       c1: uint32
#
# The created Bitfield will store three formal bitfield-groups (marked with characters a to c
# here). By default, the bitfield uses 8bit alignment, which results in 1 byte for the first
# group:
#
#       Group      Pos       Bits
#       a          0x00      8
#       b          0x01      8
#       c          0x02      32
#
# Internally, only the first group requires special parsing since the other two are structs
# without a specific bit number. This dynamic grouping model now allows us to use the power
# of struct class definitions in bitfields.
#
# This new approach enables more complect bitfield definitions. Therefore, the syntax will be
# extended:
#
#   +---------------------------------------------------+--------------------------------+
# 1.| <name> : <bits> [ - <field> ]                     | default definition             |
#   +---------------------------------------------------+--------------------------------+
# 2.| <name> : 0                                        | start new byte                 |
#   +---------------------------------------------------+--------------------------------+
# 3.| <name> : <field>                                  | custom field (no bits used)    |
#   +---------------------------------------------------+--------------------------------+
# 4.| <name> : (<field>,<factory>)                      | field with custom type factory |
#   +---------------------------------------------------+--------------------------------+
# 5.| <name> : (<bits>,<factory>[,<options>])           | bits with custom type factory  |
#   |        : (<bits>,[<options>])                     | and options                    |
#   +---------------------------------------------------+--------------------------------+
#
# The generation process will follow some implications and rules derived from this extended
# syntax. These rules are as follows:
#
#   For 1.:
#       - The default alignment is one byte (8bits). If an annotation of rule no. 2 follows,
#         eight the current byte will be filled.
#       - When the <field> is given, typeof will be called to retrieve the <factory> and
#         getbits+sizeof to retrieve the current alignment. The new alignment will be
#         ignored if a custom alignment has been set in the constructor of the BItfield.
#         If the <field> stores the B_OVERWRITE_ALIGNMENT option, the current alignment
#         will be overwritten.
#       - If the B_GROUP_END option is present, the current group will be finalized and a
#         new one will be started.
#
#   For 2.:
#       - This field definition will be removed regardless of the given name
#       - The current configured alignment will be used to fill bits up to the alignment.
#       - This field definition finalizes the current bitfield-group unless B_GROUP_KEEP
#         has been configured on the bitfield.
#
#   For 3.:
#       - The same rules as for defining fields in struct classes apply here.
#       - Additionally, this definition implies a definition of rule no. 2. The current group
#         will be finalized regardless of whether B_GROUP_KEEP has been set.
#
#   For 4.:
#       - Extension of rule no. 1 that explicitly defines the conversion factory, which must be
#         one of the following types: Type (such as int, bool) that supports the __int__ method,
#         or a type or instance of a BitfieldValueFactory.
#
#   For 5.:
#       - Same processing as for rule no. 4 but defined options (either flags or options described
#         below) can be present either as list or single element. Additional options are:
#               NewGroup: Aligns the previous group to the current alignment and creates a new one
#                         while also adding the specified bitfield entry to the new group.
#               EndGroup: Adds the bitfield entry to the current group and aligns to according to the
#                         current alignment.
#               SetAlignment: Updates the current working alignment
#         The order of specified options matters.

DEFAULT_ALIGNMENT = 8

NewGroup = B_GROUP_NEW
EndGroup = B_GROUP_END


class SetAlignment:
    def __init__(self, new_alignment: int) -> None:
        self.alignment = new_alignment

    @staticmethod
    def flag(new_alignment: int):
        return Flag("bitfield.new_alignment", new_alignment)

    def __hash__(self) -> int:
        return hash("SetAlignment")


def getbits(obj) -> int:
    __bits__ = getattr(obj, ATTR_BITS)
    return __bits__() if callable(__bits__) else __bits__


def issigned(obj) -> bool:
    return bool(getattr(obj, ATTR_SIGNED, None))


class BitfieldValueFactory:
    def __init__(self, target=None) -> None:
        self.target = target or int

    def to_int(self, obj) -> int:
        return int(obj)

    def from_int(self, value: int):
        return self.target(value)


class BitfieldEntry:
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
        return BitfieldEntry(0, 0, "<action>", action=action)

    def shift(self, value_width: int) -> int:
        bit_pos = max(0, value_width - self.bit)
        return max(bit_pos - self.width, 0)

    def is_action(self) -> bool:
        return self.action is not None

    def __repr__(self) -> str:
        if self.is_action():
            return repr(self.action)

        r = f"<Entry {self.name!r}: bit={self.bit}, width={self.width}"
        if self.factory:
            type_ = type(self.factory)
            if type_ is BitfieldValueFactory:
                type_ = int

            r = f"{r}, factory={type_.__name__}"
        return f"{r}>"


class BitfieldGroup:
    def __init__(self, bit_count: int) -> None:
        self.bit_count = bit_count
        self.entries = []

    def is_field(self) -> bool:
        return self.bit_count == -1

    def get_field(self):
        return self.entries[0]

    def set_field(self, field):
        self.entries = [field]
        self.bit_count = -1

    def align_to(self, alignment: int):
        if not self.is_field():
            pad = self.bit_count % alignment
            if pad > 0:
                self.bit_count += alignment - pad

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def get_size(self, context=None):
        if self.is_field():
            field = self.get_field()
            return field.__size__(context) if context else sizeof(field)

        return self.bit_count // 8

    def get_bits(self, context=None):
        return self.get_size(context) * 8

    def __repr__(self) -> str:
        if self.is_field():
            return repr(self.get_field())

        return f"<BitfieldGroup ({self.bit_count}) {self.entries!r}>"


class Bitfield(Struct):
    __slots__ = (
        "groups",
        "alignment",
        "_bit_pos",
        "_current_group",
        "_current_alignment",
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
        # self.__bits__ = sum(map(lambda x: x.bit_count, self.groups))

        self.groups = [group for group in self.groups if not group.is_empty()]
        del self._bit_pos
        del self._current_alignment
        del self._current_group

    def __add__(self, sequence):
        if not isinstance(sequence, Bitfield):
            raise TypeError(
                f"Attempted to add a non-bitfield struct to a bitfield! (type={type(sequence)})"
            )

        self.groups.extend(sequence.groups)
        return super(Struct, self).__add__(sequence)

    def _process_align(self, options) -> Field:
        for option in options or []:
            if self._process_alignment_option(option):
                continue

            alignment = self._current_alignment
            group = self._current_group
            if option.name in (EndGroup.name, NewGroup.name):
                # finalize current group (same effect for alignment statement)
                group.align_to(alignment)
                self._current_group = self._new_group(alignment)

        # 2.: the current group will be finalized
        if not self.has_option(B_GROUP_KEEP):
            self._current_group.align_to(self._current_alignment)
            self._current_group = self._new_group(self._current_alignment)

        return Field(Pass)

    def _process_bits(self, name: str, bits: int, factory=None, options=None) -> Field:
        if bits == 0:
            return self._process_align(options)

        entry = BitfieldEntry(self._bit_pos, bits, name, factory)
        self._bit_pos += bits
        if not self._process_options(options, entry):
            group = self._current_group
            group.entries.append(entry)
            # Adjust the size of the goup dynamically
            group.bit_count = max(group.bit_count, self._bit_pos)
        # this is only symbolic
        return Field(Int(bits))

    def _process_bits_field(self, name: str, field, options=None) -> Field:
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
            self._bit_pos, width, name, BitfieldValueFactory(typeof(field))
        )
        self._bit_pos += width
        if not self._process_options(options, entry):
            group = self._current_group
            group.entries.append(entry)
            group.bit_count = max(group.bit_count, self._bit_pos)

        if field.has_flag(B_OVERWRITE_ALIGNMENT):
            self._current_alignment = (sizeof(field) * 8) or DEFAULT_ALIGNMENT
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
            self._current_alignment = option.alignment
            return True
        elif isinstance(option, Flag):
            if option.name == "bitfield.new_alignment":
                self._current_alignment = option.value or DEFAULT_ALIGNMENT
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
                elif isinstance(factory_or_option, type) and issubclass(
                    factory_or_option, BitfieldValueFactory
                ):
                    factory = factory_or_option()
                else:
                    # treat as option
                    options = [factory_or_option]
                options.extend(extra_options)

                if isinstance(width, int):
                    # rule no. 5
                    return self._process_bits(name, width, factory, options)

                field = width
                if not isinstance(field, Field):
                    field = Field(field, order=order, arch=arch, default=default)

                return self._process_bits_field(name, field, options)

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

    def __size__(self, context) -> int:
        # size is different as our model includes correct padding
        return sum(map(lambda g: g.get_size(context), self.groups))

    def __bits__(self) -> int:
        return sum(map(lambda g: g.get_bits(), self.groups))

    def unpack_one(self, context):
        init_data = Context()
        context[CTX_OBJECT] = Context(_parent=context)
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
                if name in self._member_map_:
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

                    print(bin(raw_value), entry.shift(group.bit_count), bin(entry.low_mask))
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
                if name in self._member_map_:
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
