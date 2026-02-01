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
# pyright: reportPrivateUsage=false, reportAny=false, reportExplicitAny=false
from io import BytesIO
from collections.abc import Collection
from typing import Any, Generic
from typing_extensions import Self, override, TypeVar

from caterpillar.abc import (
    _StructLike,
    _GreedyType,
    _PrefixedType,
    _IT,
    _OT,
    _EndianLike,
    _ArchLike,
    _ContextLike,
    _ContextLambda,
    _OptionLike,
    _ContainsStruct,
    _SwitchOptionsT,
    _LengthT,
    _StreamType,
)
from caterpillar.byteorder import (
    O_DEFAULT_ARCH,
    O_DEFAULT_ENDIAN,
    LittleEndian,
    system_arch,
)
from caterpillar.exception import (
    DynamicSizeError,
    StructException,
    OptionError,
    ValidationError,
    InvalidValueError,
)
from caterpillar.options import (
    GLOBAL_FIELD_FLAGS,
    F_DYNAMIC,
)
from caterpillar.context import CTX_OFFSETS, CTX_STREAM, CTX_FIELD, CTX_VALUE, CTX_SEQ
from caterpillar import registry
from caterpillar.shared import getstruct, typeof


_T = TypeVar("_T")


def singleton(cls: type[_T]) -> _T:
    """Simple wrapper to enable singleton structs."""
    return cls()


# Constant representing an invalid default value
INVALID_DEFAULT: object = object()
DEFAULT_OPTION: object = object()


class Field(Generic[_IT, _OT]):
    """Represents a field in a data structure.

    :param struct: The structure or callable used to define the field's type.
    :param order: Byte order for the field (default: SysNative).
    :param offset: Field offset or callable (default: -1, meaning no explicit offset).
    :param flags: Optional set of flags associated with the field.
    :param amount: The number of elements if this field is a sequence (default: 0).
    :param options: A dictionary representing a switch-case mapping.
    :param condition: A boolean or callable determining whether the field is active.
    :param arch: Architecture specification (default: system_arch).
    :param default: The default value (default: INVALID_DEFAULT).
    :param bits: Bit size if the field is bit-packed.
    """

    def __init__(
        self,
        struct: _StructLike[_IT, _OT] | _ContextLambda[_OT] | _ContainsStruct[_IT, _OT],
        order: _EndianLike | None = None,
        offset: _ContextLambda[int] | int = -1,
        flags: set[_OptionLike] | None = None,
        amount: _LengthT = 0,
        options: _SwitchOptionsT | None = None,
        condition: _ContextLambda[bool] | bool = True,
        arch: _ArchLike | None = None,
        default: object = INVALID_DEFAULT,
        bits: _ContextLambda[int] | int | None = None,
    ) -> None:
        # Cached flags to optimize packing/unpacking performance
        self._is_lambda: bool = False
        self._has_cond: bool = False
        self._cond_is_lambda: bool = False
        self._is_seq: bool = False
        self._keep_pos: bool = True
        self._has_offset: bool = False
        self._offset_is_lambda: bool = False
        self._amount_is_lambda: bool = False
        self._switch_is_lambda: bool = False
        self._switch_has_default: bool = False

        # private variable initialization
        self.__struct = None
        self.__condition = None
        self.__flags = None
        self.__offset = None
        self.__amount = None
        self.__options = None  # Historically named; represents switch mappings
        self.__order = None
        self.__arch = None

        # initialization via property setters
        self.struct = struct
        self.condition = condition
        self.order = order
        self.flags = set(flags or [])
        self.bits: _ContextLambda[int] | int | None = bits
        self.arch = arch
        self.offset = offset
        self.amount = amount or None
        self.options = options

        # INVALID_DEFAULT indicates that no default was explicitly set;
        # allows None to be used as a valid default
        self.default: object = default

    # -- Property Definitions (Input validation not enforced) --

    @property
    def struct(self) -> _StructLike[_IT, _OT] | _ContextLambda[_OT]:
        """
        The internal structure for this field.
        """
        return self.__struct  # pyright: ignore[reportReturnType]

    # fmt: off
    @struct.setter
    def struct(
        self,
        value: _StructLike[_IT, _OT] | _ContextLambda[_OT] | _ContainsStruct[_IT, _OT],  # pyright: ignore[reportPropertyTypeMismatch]
    ) -> None:
        self.__struct = getstruct(value) or value
        # pre-computed state of this field
        self._is_lambda = callable(self.__struct)
    # fmt: on

    @property
    def condition(self) -> _ContextLambda[bool] | bool:
        """
        The field's condition expression or value.
        """
        return self.__condition  # pyright: ignore[reportReturnType]

    @condition.setter
    def condition(self, value: _ContextLambda[bool] | bool):
        self.__condition = value
        self._has_cond = value not in (True, None)
        self._cond_is_lambda = callable(value)

    @property
    def flags(self) -> set[_OptionLike]:
        """The set of flags associated with this field."""
        return self.__flags  # pyright: ignore[reportReturnType]

    @flags.setter
    def flags(self, value: set[_OptionLike]) -> None:
        self.__flags = value

    def add_flag(self, flag: _OptionLike) -> None:
        """
        Adds a flag to this field.

        :param flag: The flag to add.

        .. versionadded:: 2.6.0
        """
        self.flags.add(flag)

    def has_flag(self, flag: _OptionLike[Any]) -> bool:
        """Checks whether this field stores the given flag.

        :param flag: the flag to lookup
        :type flag: Flag
        :return: true if this flag has been found
        :rtype: bool
        """
        return flag in self.flags or flag in GLOBAL_FIELD_FLAGS

    def remove_flag(self, flag: _OptionLike) -> None:
        """
        Removes a flag from this field.

        :param flag: The flag to remove.

        .. versionadded:: 2.6.0
        """
        self.flags.discard(flag)

    @property
    def offset(self) -> _ContextLambda[int] | int:
        """The field's offset."""
        return self.__offset  # pyright: ignore[reportReturnType]

    @offset.setter
    def offset(self, value: _ContextLambda[int] | int):
        self.__offset = value
        self._has_offset = value not in (-1, None)
        self._offset_is_lambda = callable(value)
        self._keep_pos = value in (-1, None)

    @property
    def amount(self) -> _LengthT | None:
        """The repetition count for this field."""
        return self.__amount

    @amount.setter
    def amount(self, value: _LengthT | None):
        self.__amount = value
        self._amount_is_lambda = callable(value)
        self._is_seq = (value not in (0, None)) or self._amount_is_lambda

    @property
    def options(self) -> _SwitchOptionsT | None:
        """The switch-case options dictionary."""
        return self.__options

    @options.setter
    def options(self, value: _SwitchOptionsT | None):
        self.__options = value
        self._switch_is_lambda = callable(value)
        self._switch_has_default = (
            bool(value)
            and not self._switch_is_lambda
            and DEFAULT_OPTION in value  # pyright: ignore[reportOperatorIssue]
        )

    @property
    def order(self) -> _EndianLike:
        return self.__order or O_DEFAULT_ENDIAN.value or LittleEndian

    @order.setter
    def order(
        self, value: _EndianLike | None  # pyright: ignore[reportPropertyTypeMismatch]
    ) -> None:
        self.__order: _EndianLike | None = value

    def has_order(self) -> bool:
        return bool(self.__order)

    @property
    def arch(self) -> _ArchLike:
        return self.__arch or O_DEFAULT_ARCH.value or system_arch

    @arch.setter
    def arch(
        self, value: _ArchLike | None  # pyright: ignore[reportPropertyTypeMismatch]
    ) -> None:
        self.__arch = value

    def has_arch(self) -> bool:
        return bool(self.__arch)

    def _verify_context_value(
        self, value: object, expected: type | tuple[type, ...]
    ) -> None:
        """
        Verifies that a value is either of the expected type(s) or is a callable.
        Used to validate inputs for context-aware fields.

        :param value: The value to validate.
        :param expected: A type or tuple of valid types.
        :raises TypeError: If validation fails.
        """
        # As the offset value or amount may be dynamic, we have to candidate
        # types. There should be an error if none applies.
        if not isinstance(value, expected) and not callable(value):
            raise TypeError(
                f"Expected a valid value or context lambda, got {type(value)}"
            )

    # --- Operator Overloads ---

    def __or__(self, flag: _OptionLike) -> Self:  # add flags
        """
        Adds a flag using the '|' operator.

        :param flag: The flag to add.
        :return: The updated Field instance.
        """
        self.add_flag(flag)
        return self

    def __xor__(self, flag: _OptionLike) -> Self:  # remove flags:
        """
        Removes a flag using the '^' operator.

        :param flag: The flag to remove.
        :return: The updated Field instance.
        """
        self.remove_flag(flag)
        return self

    def __matmul__(self, offset: _ContextLambda[int] | int) -> Self:
        """
        Sets the field's offset using the '@' operator.

        :param offset: The offset value (int or callable).
        :return: The updated Field instance.
        """
        self._verify_context_value(offset, int)
        self.offset = offset
        return self

    def __getitem__(self, dim: _LengthT) -> "Field[Collection[_IT], Collection[_OT]]":
        """
        Sets the number of elements using the indexing operator (e.g.,
        field[3]).

        :param dim: Repetition count or dynamic type.
        :return: The updated Field instance.
        """
        self._verify_context_value(
            dim, (_GreedyType, int, _PrefixedType, _ContextLambda)
        )
        self.amount = dim
        return self  # pyright: ignore[reportReturnType]

    def __rshift__(self, switch: _SwitchOptionsT) -> Self:
        """
        Defines switch-case mappings using the '>>' operator.

        :param switch: A dictionary of options.
        :return: The updated Field instance.
        """
        self._verify_context_value(switch, dict)
        self.options = switch
        return self

    def __floordiv__(self, condition: _ContextLambda[bool] | bool) -> Self:
        """
        Sets the field's condition using the '//' operator.

        :param condition: A boolean or callable.
        :return: The updated Field instance.
        """
        self._verify_context_value(condition, bool)
        self.condition = condition
        return self

    def __rsub__(self, bits: _ContextLambda[int] | int) -> Self:
        """
        Sets the number of bits for bit-packed fields using the reverse '-'
        operator.

        :param bits: Bit width (int or callable).
        :return: The updated Field instance.
        """
        self._verify_context_value(bits, int)
        self.bits = bits
        return self

    def __set_byteorder__(self, order: _EndianLike) -> Self:
        """
        Explicitly sets the byte order for this field.

        :param order: A ByteOrder instance.
        :return: The updated Field instance.
        """
        self.order = order
        return self

    def __type__(self) -> type:
        """
        Returns the resolved type of the field, typically from the struct.

        :return: The field type.
        """
        return self.get_type()

    __ixor__ = __xor__  # pyright: ignore[reportUnannotatedClassAttribute]
    __ior__ = __or__  # pyright: ignore[reportUnannotatedClassAttribute]
    __ifloordiv__ = __floordiv__  # pyright: ignore[reportUnannotatedClassAttribute]
    __irshift__ = __rshift__  # pyright: ignore[reportUnannotatedClassAttribute]
    __imatmul__ = __matmul__  # pyright: ignore[reportUnannotatedClassAttribute]
    __isub__ = __rsub__  # pyright: ignore[reportUnannotatedClassAttribute]

    def is_seq(self) -> bool:
        """Returns whether this field is sequential.

        :return: whether this field is sequental
        :rtype: bool
        """
        return self._is_seq

    def is_enabled(self, context: _ContextLike) -> bool:
        """Evaluates the condition of this field.

        :param context: the context on which to operate
        :type context: _ContextLike
        :return: ``True``, if this field is enabled
        :rtype: bool
        """
        if not self._has_cond:
            return True

        return self.condition(context) if self._cond_is_lambda else self.condition

    def has_condition(self) -> bool:
        """Returns whether this field is linked to a condition"""
        return self._has_cond

    def length(self, context: _ContextLike) -> _GreedyType | _PrefixedType | int:
        """Calculates the sequence length of this field.

        :param context: the context on which to operate
        :type context: _ContextLike
        :raises DynamicSizeError: if this field has a dynamic size
        :return: the number of elements
        :rtype: Union[int, _GreedyType]
        """
        try:
            return self.amount(context) if self._amount_is_lambda else self.amount
        except Exception as exc:
            raise DynamicSizeError("Dynamic sized field!", context) from exc

    def get_struct(self, value: object, context: _ContextLike) -> _StructLike[_IT, _OT]:
        """Returns the struct from stored options.

        :param value: the unpacked or packed value
        :type value: Any
        :param context: the current context
        :type context: _ContextLike
        :return: the struct that packs or unpacks the data
        :rtype: _StructLike
        """
        # treat 'value' as the key of specified options
        if self._switch_is_lambda:
            struct: _StructLike[_IT, _OT] = self.options(value, context)
        else:
            if value not in self.options and not self._switch_has_default:
                raise OptionError(f"Option {value!r} not found!", context)

            struct = self.options.get(value) or self.options.get(DEFAULT_OPTION)

        if struct is None:
            # The struct must be non-null
            raise InvalidValueError(
                f"Could not find switch value for: {value!r}", context
            )

        return getstruct(struct) or struct  # pyright: ignore[reportUnknownVariableType]

    def get_offset(self, context: _ContextLike) -> int:
        """Returns the offset position of this field"""
        return self.offset(context) if self._offset_is_lambda else self.offset

    def get_type(self) -> type:
        """Returns the annotation type for this field

        :return: the annotation type
        :rtype: type
        """
        if not self.options:
            type_ = typeof(self.struct)
            return type_ if not self.is_seq() else list[type_]

        # We construct a Union type hint as an alternative:
        if self._switch_is_lambda:
            return object

        return_type = object
        for switch_type in self.options.values():
            return_type = return_type | typeof(switch_type)

        return return_type  # pyright: ignore[reportReturnType]

    def get_name(self) -> str:
        """Returns the name of this field.

        .. versionchanged:: 2.8.0
            now always returns a string
        """
        return getattr(self, "__name__", "_")

    # IO related stuff
    def __unpack__(self, context: _ContextLike) -> _OT:
        """Reads packed data from the given stream.

        This method returns nothing if this field is disabled and applies switch if
        additional options are configured.

        :param context: the current context
        :type context: _ContextLike
        :return: the parsed data
        """
        stream: _StreamType = context[CTX_STREAM]
        if self._has_cond and not self.is_enabled(context):
            # Disabled fields or context lambdas won't pack any data
            return
        # fmt: off
        # Using this inlined version of self.is_seq(), we reduce the amount of
        # calls made to the method and save A LOT of time.
        # pylint: disable-next=protected-access
        context[CTX_SEQ] = self._is_seq
        # pylint: disable-next=protected-access
        keep_pos: bool = self._keep_pos
        if not self._is_lambda:  # REVISIT: maybe hardcode this
            if not keep_pos:
                fallback: int = stream.tell()

            if self._has_offset:
                offset: int = self.offset(context) if self._offset_is_lambda else self.offset
                stream.seek(offset)  # pyright: ignore[reportUnusedCallResult]

            context[CTX_FIELD] = self
            # Switch is applicable AFTER we parsed the first value
            try:
                value = self.struct.__unpack__(context)
                if not keep_pos:
                    stream.seek(fallback)  # pyright: ignore[reportUnusedCallResult]
            # pylint: disable-next=broad-exception-caught
            except Exception as exc:
                if not isinstance(exc, StructException):
                    exc = StructException(str(exc), context)
                # Any exception leads to a default value if configured
                value = self.default
                if value is INVALID_DEFAULT or isinstance(exc, ValidationError):
                    raise exc
        else:
            # Context functions should be executed with top priority
            value: _OT = self.struct(context)  # pyright: ignore[reportUnknownVariableType]

        # unpack using switch
        if self.options:
            struct = self.get_struct(value, context)
            # The "keep_position" flag is not applicable here. Configure a field to keep the
            # position afterward.
            context[CTX_VALUE] = value
            value = struct.__unpack__(context)
        # fmt; on
        return value

    def __pack__(self, obj: _IT, context: _ContextLike) -> None:
        """Writes the given object to the provided stream.

        There are several options associated with this function. First, disabled
        fields will never pack any data. Next, if an offset position is specified,
        this method will first jump to that position and then parse all data.

        If this field contains a sequential type, it will automatically iterate over
        all elements in ``obj``. The final stream position will be reset if the user
        flag ``KEEP_POSITION`` is not found.

        :param obj: the value to write
        :type obj
        :param context: the current context with a qualified path
        :type context: _ContextLike
        :raises TypeError: if the value is not iterable but this field is marked
                           to be sequential
        """
        # TODO: revisit code
        if self._has_cond and not self.is_enabled(context):
            # Disabled fields or context lambdas won't pack any data
            return

        stream: _StreamType = context[CTX_STREAM]
        keep_pos = self._keep_pos
        has_offset = self._has_offset
        context[CTX_FIELD] = self
        # pylint: disable-next=protected-access
        context[CTX_SEQ] = self._is_seq
        if not keep_pos or has_offset:
            fallback = stream.tell()

        if has_offset:
            # TODO: implement F_OFFSET_OVERRIDE
            # We write the current field into a temporary memory buffer
            # and add it after all processing hasbeen finished.
            offset: int = (
                self.offset(context) if self._offset_is_lambda else self.offset
            )
            base_stream = stream
            stream = BytesIO()
            context[CTX_STREAM] = stream

        if not self.options:
            _ = (
                self.struct.__pack__(obj, context)
                if not self._is_lambda
                else self.struct(context)
            )
        else:
            # Just hand over the input value if the struct is not a lambda
            context[CTX_VALUE] = obj
            value = self.struct(context) if self._is_lambda else obj
            if not self._is_lambda:
                # support for non-context lambdas with switch statements
                self.struct.__pack__(value, context)
            if self.options is not None:
                struct = self.get_struct(value, context)
                struct.__pack__(obj, context)

        if not has_offset and not keep_pos:
            # The position shouldn't be persisted reset the stream
            stream.seek(fallback)  # pyright: ignore[reportUnusedCallResult]

        if has_offset:
            # Place the stream into the internal offset map
            context._root[CTX_OFFSETS][offset] = stream.getbuffer()
            context[CTX_STREAM] = base_stream

    def __size__(self, context: _ContextLike) -> int:
        """Calculates the size of this field.

        There are several situations to bear in mind when executing this function:

         1. If this field is disabled, it will return zero as its size.
         2. Next, dynamic fields do not store a size and DynamicSizeError will be thrown.
         3. Sequential fields will multiply the struct's size with the amount of elements.

         :param context: the operation context
         :type context: _ContextLike
         :raises DynamicSizeError: if this field has a dynamic size
         :return: the calculated size
         :rtype: int
        """
        # 1. If this field is disabled, it will return zero as its size
        if not self.is_enabled(context):
            return 0

        # 2. Next, dynamic fields does not store a size
        if self.has_flag(F_DYNAMIC):
            raise DynamicSizeError("Dynamic sized field!", context)

        context[CTX_FIELD] = self
        context[CTX_SEQ] = self._is_seq

        # 3. We should gather the element count if this field stores
        # a sequential element
        count = 1
        if context[CTX_SEQ]:
            count = self.length(context)
            if isinstance(count, (_GreedyType, _PrefixedType)):
                raise DynamicSizeError(
                    "Greedy or prefixed fields does not have a fixed size!", context
                )

        struct = self.struct
        if self.options:
            if not callable(self.struct):
                raise DynamicSizeError(
                    "Switch statement without ContextLambda is danymic sized!", context
                )
            try:
                value = self.struct(context)
            except Exception as exc:
                raise DynamicSizeError("Dynamic sized switch field!", context) from exc
            struct = self.get_struct(value, context)

        size = struct.__size__(context)
        return count * size

    # representation, maybe revisit
    @override
    def __str__(self) -> str:
        name = self.get_name() or "<unnamed>"
        offset = f", offset={self.offset}" if self._has_offset else ""
        return (
            f"Field({name!r}, arch={self.arch.name!r}, order={self.order.name!r}, "
            f"seq={self.is_seq()}, struct={self.struct!r}, cond={self.condition is not True}, "
            f"options={bool(self.options)}{offset})"
        )

    @override
    def __repr__(self) -> str:
        return self.__str__()


# --- private type converter ---
@registry.TypeConverter(_StructLike)
def _type_converter(annotation: _StructLike[_IT, _OT], kwargs: Any) -> Field[_IT, _OT]:
    # REVISIT: more options ?
    arch: _ArchLike | None = kwargs.pop("arch", None)
    order: _EndianLike | None = kwargs.pop("order", None)
    return Field(annotation, order=order, arch=arch)


registry.annotation_registry.append(_type_converter)


class _CallableTypeConverter(registry.TypeConverter):
    @override
    def matches(self, annotation: object) -> bool:
        # must be a callable but not a type
        return callable(annotation) and not isinstance(annotation, type)

    @override
    def convert(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, annotation: _ContextLambda[_OT], kwargs: Any
    ) -> Field[None, _OT]:
        arch: _ArchLike | None = kwargs.pop("arch", None)
        order: _EndianLike | None = kwargs.pop("order", None)
        # callables are treates as context lambdas
        return Field(annotation, order=order, arch=arch)


registry.annotation_registry.append(_CallableTypeConverter())
