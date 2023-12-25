# Copyright (C) MatrixEditor 2023
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
from typing import Optional, Any, Dict
from typing import Iterable, Tuple
from typing import Self, List
from dataclasses import dataclass, field as dcfield

from caterpillar.abc import _StructLike, _ContextLike, _StreamType, typeof
from caterpillar.byteorder import (
    Arch,
    ByteOrder,
    byteorder,
    get_system_arch,
    LittleEndian,
)
from caterpillar.options import (
    Flag,
    GLOBAL_BITFIELD_FLAGS,
    GLOBAL_STRUCT_OPTIONS,
    GLOBAL_UNION_OPTIONS,
)
from caterpillar.fields import (
    Field,
    uint8,
    uint16,
    uint32,
    uint64,
    uint128,
    boolean,
    Pass,
)
from caterpillar.exception import ValidationError, DelegationError
from caterpillar.context import Context, CTX_PATH, CTX_OBJECT, CTX_STREAM

from ._struct import Struct

BitTuple = Tuple[int, int]


BITS_ATTR = "__bits__"
SIGNED_ATTR = "__signed__"


def getbits(obj: Any) -> int:
    __bits__ = getattr(obj, BITS_ATTR)
    return __bits__() if callable(__bits__) else __bits__

def issigned(obj: Any) -> bool:
    return bool(getattr(obj, SIGNED_ATTR, None))


@dataclass(frozen=True)
class BitFieldGroup:
    size: int
    pos: int
    fields: Dict[BitTuple, Field] = dcfield(default_factory=dict)


class Bitfield(Struct):
    groups: List[BitFieldGroup]

    def __init__(
        self,
        model: type,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        options: Iterable[Flag] = None,
        field_options: Iterable[Flag] = None,
    ) -> None:
        self.groups: List[BitFieldGroup] = []
        # These fields remain private and will be deleted after processing
        self._bit_pos: int = 0
        self._abs_bit_pos: int = 0
        self._current_group: BitFieldGroup = None

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
        self._length = self._abs_bit_pos

        del self._bit_pos
        del self._abs_bit_pos
        del self._current_group

    def __add__(self, other: "BitField") -> Self:
        if not isinstance(other, Bitfield):
            raise ValidationError(
                f"Attempted to add a non-bitfield struct to a bitfield! (type={type(other)})"
            )
        return super(Struct, self).__add__(other)

    def _process_field(
        self, name: str, annotation: Any, default: Optional[Any]
    ) -> Field:
        """
        Process a field in the model.

        :param name: The name of the field.
        :param annotation: The annotation of the field.
        :param default: The default value of the field.
        :return: The processed field.
        """

        # Fields can be defined as follows:
        #    name : bit_count [ - struct ] [ = default_value ]
        # or
        #    name : struct [ = default_value ]
        struct: _StructLike = None
        field: Field = None

        order = byteorder(annotation, self.order)
        group: BitFieldGroup = self._current_group
        arch = self.arch or get_system_arch()

        width = 0
        if group is None:
            # First, specify the current group and add it to the rest of
            # the internal representation.
            group = BitFieldGroup(8, self._abs_bit_pos)
            self.groups.append(group)
            self._current_group = group

        if isinstance(annotation, int):
            # CASE 1: Only the bit amount is specified. We take the current group
            # into consideration and decide whether we have to apply a padding.
            # TODO: cleanup
            struct = uint8  # this struct is only used to infer the right type
            if 8 < annotation <= 16:
                struct = uint16
            elif 16 < annotation <= 32:
                struct = uint32
            elif 32 < annotation <= 64:
                struct = uint64
            elif 64 < annotation <= 128:
                struct = uint128
            elif annotation == 1:
                struct = boolean
            if annotation != 0:
                width = annotation
            else:
                # Special case: a zero indicates we have to start a new byte. To
                # accomplish that, we simply create a new BitFieldGroup. The padding
                # is generated by moving the internal absolute bit position forwards.
                self._current_group = BitFieldGroup(8, self._abs_bit_pos)
                width = 8 - self._abs_bit_pos % 8
                struct = Pass  # NoneType will be inferred

        elif isinstance(annotation, Field):
            # CASE 2: the field has been defined using a type specifier.
            field = annotation
            if field.bits is None:
                # We have to use a special method to calculate the amount of this this
                # field takes.
                try:
                    width = getbits(field.struct)
                except ValueError as exc:
                    raise ValidationError(
                        f"Field {name!r} does not specify a bit width!"
                    ) from exc
            else:
                width = field.bits

        elif isinstance(annotation, _StructLike):
            # CASE 3: Only the struct is given without a bit width
            struct = annotation
            try:
                # The same applies here: the struct MUST specify a bit width
                width = getbits(struct)
            except ValueError as exc:
                raise ValidationError(
                    f"Field {name!r} does not specify a bit width!"
                ) from exc

        if struct is not None:
            field = Field(struct, order, arch=arch, default=default)

        if field is None:
            raise ValidationError(
                f"Field {name!r} could not be created: {annotation!r}"
            )
        field.default = default
        field.order = self.order or field.order
        field.arch = self.arch or field.arch
        field.bits = field.bits or width
        field.flags.update(self.field_options)

        # Now, we have to check whether a new byte has to be started
        if group.size - self._bit_pos < width:
            if field.bits is None:
                # Only type specified, we take its bit count
                size = width
            else:
                leftover = width % 8
                size = width + ((8 - leftover) if leftover > 0 else 0)
            group = BitFieldGroup(size, self._abs_bit_pos)
            self._current_group = group
            self.groups.append(group)
            self._bit_pos = 0

        group.fields[(self._bit_pos, width)] = field
        self._bit_pos += width
        self._abs_bit_pos += width
        return field

    def _included(self, name: str, default: Optional[Any], annotation: Any) -> bool:
        if not super()._included(name, default, annotation):
            return False

        if isinstance(annotation, int) and annotation == 0:
            # padding should be ignored
            return False
        return True

    def group(self, bit_index: int) -> Optional[BitFieldGroup]:
        grp: BitFieldGroup = None
        for candidate in self.groups:
            if bit_index > candidate.pos:
                break
            grp = candidate
        return grp

    def __size__(self, context: _ContextLike) -> int:
        # The size of a bitfield is alsways static
        return self._length

    def unpack_one(self, context: _ContextLike) -> Optional[Any]:
        # At first, we define the object context where the parsed values
        # will be stored
        stream: _StreamType = context[CTX_STREAM]
        init_data: Dict[str, Any] = Context()
        context[CTX_OBJECT] = Context(_parent=context)
        base_path = context[CTX_PATH]

        for i, group in enumerate(self.groups):
            # each group specifies the fields we are about to unpack. But first, we have
            # to read the bits from the stream
            order = "little" if self.order == LittleEndian else "big"
            value = int.from_bytes(stream.read(group.size // 8), byteorder=order)

            for bit_info, field in group.fields.items():
                name: str = field.get_name()
                context[CTX_PATH] = ".".join([base_path, f"<{i}>", name])
                pos, width = bit_info
                # The field should be ignored if it is not within the
                # member map (this usually means we have a padding field)
                if name not in self._member_map_:
                    continue

                low_mask = (1 << width) - 1
                if width == 1:
                    mask = low_mask << pos
                    init_data[name] = bool(value & mask)
                else:
                    field_value: int = (value >> pos) & low_mask
                    factory = typeof(field.struct)
                    if factory not in (type(None), Any):
                        field_value = factory(field_value)

                    # Finally, apply the new value
                    init_data[name] = field_value

        obj = self.model(**init_data)
        return obj

    def pack_one(self, obj: Any, context: _ContextLike) -> None:
        stream: _StreamType = context[CTX_STREAM]
        base_path: str = context[CTX_PATH]
        for i, group in enumerate(self.groups):
            # The same applies here, but we convert all values to int instead of reading
            # them from the stream
            order = "little" if self.order == LittleEndian else "big"
            value = 0
            for bit_info, field in group.fields.items():
                # Setup the field's context
                name: str = field.get_name()
                context[CTX_PATH] = ".".join([base_path, f"({i})", name])
                pos, width = bit_info
                # Padding is translated into zeros
                if name not in self._member_map_:
                    continue

                field_value = self.get_value(obj, name, field) or 0
                # Here's the tricky part: we have to convert all values to int
                # without knowing their type. We make use of Python's data model,
                # which defines a function particularly for this use-case: __int__
                #
                # See https://docs.python.org/3/reference/datamodel.html#object.__int__
                try:
                    # REVISIT: what about the field's width
                    value |= int(field_value) << pos
                except NotImplementedError as exc:
                    raise DelegationError(
                        f"Field {name!r} does not support to-int conversio!"
                    ) from exc
            # REVISIT: is this cheating?
            stream.write(value.to_bytes(group.size // 8, byteorder=order))


def _make_bitfield(
    cls: type,
    options: Iterable[Flag],
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Iterable[Flag] = None,
) -> type:
    _ = Bitfield(
        cls, order=order, arch=arch, options=options, field_options=field_options
    )
    return cls


def bitfield(
    cls: type = None,
    /,
    *,
    options: Iterable[Flag] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Iterable[Flag] = None,
):
    def wrap(cls):
        return _make_bitfield(
            cls, options=options, order=order, arch=arch, field_options=field_options
        )

    if cls is not None:
        return _make_bitfield(
            cls, options=options, order=order, arch=arch, field_options=field_options
        )

    return wrap
