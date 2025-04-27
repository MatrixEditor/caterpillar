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
from typing import Self, Union, Set, Any, Dict, Optional, List, Callable
from io import BytesIO
from caterpillar.abc import (
    _StructLike,
    _ContextLambda,
    _Switch,
    _StreamType,
    _ContextLike,
    _GreedyType,
    _PrefixedType,
    hasstruct,
    getstruct,
    typeof,
)
from caterpillar.byteorder import ByteOrder, SysNative, Arch, system_arch
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
    F_KEEP_POSITION,
    F_SEQUENTIAL,
    Flag,
)
from caterpillar.context import CTX_OFFSETS, CTX_STREAM
from caterpillar.context import CTX_FIELD, CTX_POS
from caterpillar.context import CTX_VALUE, CTX_SEQ
from caterpillar import registry


def singleton(cls):
    """Simple wrapper to enable singleton structs."""
    return cls()


# Constant representing an invalid default value
INVALID_DEFAULT = object()
DEFAULT_OPTION = object()


# @dataclass(init=False)
class Field:
    """Represents a field in a data structure."""

    struct: Union[_StructLike, _ContextLambda]
    """
    Stores a reference to the actual parsing struct that will be used to parse or
    build our data. This attribute is never null.
    """

    order: ByteOrder
    """
    An automatically inferred or explicitly specified byte order. Note that this
    attribute may have no impact on the underlying struct. The default byte order
    is ``SysNative``.
    """

    offset: Union[_ContextLambda, int]
    """
    Using the ``@`` operator an offset can be assigned to a field. If set, the
    stream will be reset and set to the original position.

    The minus one indicates that no offset has been associated with this field.
    """

    flags: Dict[int, Flag]
    """
    Additional options that can be enabled using the logical OR operator ``|``.

    Note that there are default options that will be set automatically:

    * ``keep_position``:
        Persists the streams position after parsing data using the underlying
        struct. In relation to ``offset``, this option will reset the stream to
        its original position if deactivated.
    * ``dynamic``:
        Specifies that this field does not store a constant size.
    * ``sequential``:
        An automatic flag that indicates this field stores a sequential struct.
    """

    amount: Union[_ContextLambda, int, _GreedyType, _PrefixedType]
    """
    A constant or dynamic value to represent the amount of structs. Zero indicates
    there are no sequence types associated with this field.
    """

    options: Union[_Switch, Dict[Any, _StructLike], None]
    """
    An extra attribute that stores additional options that can be translates as a
    switch statement.
    """

    condition: Union[_ContextLambda, bool]
    """
    Given optional execution this attribute should be used to return a boolean value
    that decides whether the value of this field should be set. Using ``//`` the
    condition can be set during class declaration.
    """

    arch: Arch
    """
    The field's architecture (inferred or explicitly specified).
    """

    default: Optional[Any]
    """
    The configured default value.
    """

    bits: Union[_ContextLambda, int, None]
    """
    The configured bits.
    """

    __slots__ = (
        "struct",
        "order",
        "flags",
        "bits",
        "arch",
        "amount",
        "options",
        "condition",
        "default",
        "offset",
        "__name__",
    )

    def __init__(
        self,
        struct: Union[_StructLike, _ContextLambda],
        order: ByteOrder | None = None,
        offset: Union[_ContextLambda, int] = -1,
        flags: Set[Flag] = None,
        amount: Union[_ContextLambda, int, _PrefixedType] = 0,
        options: Union[_Switch, Dict[Any, _StructLike], None] = None,
        condition: Union[_ContextLambda, bool] = True,
        arch: Arch = None,
        default: Optional[Any] = INVALID_DEFAULT,
        bits: Union[_ContextLambda, int, None] = None,
    ) -> None:
        # NOTE: we use a custom init method to automatically set flags
        self.struct = struct
        self.order = order or SysNative
        self.flags = {hash(x): x for x in flags or set([F_KEEP_POSITION])}
        self.bits = bits

        self.arch = arch or system_arch
        # this will unset KEEP_POSITION if configured
        self.__matmul__(offset)
        if amount:
            self.__getitem__(amount)
        else:
            self.amount = 1
        self.options = options
        self.condition = condition
        # NOTE: we use INVALID_DEFAULT as disabled default value indicator, so
        # that None is still usable as default
        self.default = default

    def _verify_context_value(
        self, value: Union[_ContextLambda, Any], expected: type
    ) -> None:
        # As the offset value or amount may be dynamic, we have to candidate
        # types. There should be an error if none applies.
        if not isinstance(value, expected) and not callable(value):
            raise TypeError(
                f"Expected a valid value or context lambda, got {type(value)}"
            )

    def __or__(self, flag: Flag) -> Self:  # add flags
        if not isinstance(flag, Flag):
            raise TypeError(f"Expected a flag, got {type(flag)}")

        self.flags[hash(flag)] = flag
        return self

    def __xor__(self, flag: Flag) -> Self:  # remove flags:
        self.flags.pop(hash(flag), None)
        return self

    def __matmul__(self, offset: Union[_ContextLambda, int]) -> Self:
        self._verify_context_value(offset, int)
        self.offset = offset
        # This operation automatically removes the "keep_position"
        # flag. It has to be set manually.
        if self.offset != -1:
            self.flags.pop(F_KEEP_POSITION._hash_, None)
        return self

    def __getitem__(self, dim: Union[_ContextLambda, int, _GreedyType]) -> Self:
        self._verify_context_value(dim, (_GreedyType, int, _PrefixedType))
        self.amount = dim
        if self.amount != 0:
            # pylint: disable-next=protected-access
            self.flags[F_SEQUENTIAL._hash_] = F_SEQUENTIAL
        return self

    def __rshift__(self, switch: Union[_Switch, dict]) -> Self:
        if not isinstance(switch, dict) and not callable(switch):
            raise TypeError(f"Expected a valid switch context, got {type(switch)}")

        self.options = switch
        return self

    def __floordiv__(self, condition: Union[_ContextLambda, bool]) -> Self:
        self._verify_context_value(condition, bool)
        self.condition = condition
        return self

    def __rsub__(self, bits: Union[_ContextLambda, int]) -> Self:
        self._verify_context_value(bits, int)
        self.bits = bits
        return self

    def __set_byteorder__(self, order: ByteOrder) -> Self:
        self.order = order
        return self

    def __type__(self) -> type:
        return self.get_type()

    __ixor__ = __xor__
    __ior__ = __or__
    __ifloordiv__ = __floordiv__
    __irshift__ = __rshift__
    __imatmul__ = __matmul__
    __isub__ = __rsub__

    def is_seq(self) -> bool:
        """Returns whether this field is sequential.

        :return: whether this field is sequental
        :rtype: bool
        """
        # pylint: disable-next=protected-access
        return F_SEQUENTIAL._hash_ in self.flags

    def is_enabled(self, context: _ContextLike) -> bool:
        """Evaluates the condition of this field.

        :param context: the context on which to operate
        :type context: _ContextLike
        :return: ``True``, if this field is enabled
        :rtype: bool
        """
        return self.condition(context) if callable(self.condition) else self.condition

    def has_condition(self) -> bool:
        """Returns whether this field is linked to a condition"""
        return self.condition is not True

    def has_flag(self, flag: Flag) -> bool:
        """Checks whether this field stores the given flag.

        :param flag: the flag to lookup
        :type flag: Flag
        :return: true if this flag has been found
        :rtype: bool
        """
        # pylint: disable-next=protected-access
        return flag._hash_ in self.flags or flag in GLOBAL_FIELD_FLAGS

    def length(self, context: _ContextLike) -> Union[int, _GreedyType, _PrefixedType]:
        """Calculates the sequence length of this field.

        :param context: the context on which to operate
        :type context: _ContextLike
        :raises DynamicSizeError: if this field has a dynamic size
        :return: the number of elements
        :rtype: Union[int, _GreedyType]
        """
        try:
            if isinstance(self.amount, (int, _GreedyType, _PrefixedType)):
                return self.amount

            return self.amount(context)
        except Exception as exc:
            raise DynamicSizeError("Dynamic sized field!", context) from exc

    def get_struct(self, value: Any, context: _ContextLike) -> _StructLike:
        """Returns the struct from stored options.

        :param value: the unpacked or packed value
        :type value: Any
        :param context: the current context
        :type context: _ContextLike
        :return: the struct that packs or unpacks the data
        :rtype: _StructLike
        """
        # treat 'value' as the key of specified options
        if isinstance(self.options, dict):
            if value not in self.options and DEFAULT_OPTION not in self.options:
                raise OptionError(f"Option {str(value)!r} not found!", context)

            struct = self.options.get(value, None) or self.options.get(DEFAULT_OPTION)
        else:
            struct = self.options(value, context)

        if struct is None:
            # The struct must be non-null
            raise InvalidValueError(
                f"Could not find switch value for: {value!r}", context
            )

        if hasstruct(struct):
            return getstruct(struct)
        return struct

    def get_offset(self, context: _ContextLike) -> int:
        """Returns the offset position of this field"""
        return self.offset(context) if callable(self.offset) else self.offset

    def get_type(self) -> type:
        """Returns the annotation type for this field

        :return: the annotation type
        :rtype: type
        """
        if not self.options:
            type_ = typeof(self.struct)
            return type_ if not self.is_seq() else List[type_]

        # We construct a Union type hint as an alternative:
        if callable(self.options):
            return Any

        types = [typeof(s) for s in self.options.values()]
        return Union[*types, Any]

    def get_name(self) -> Optional[str]:
        return getattr(self, "__name__", None)

    # IO related stuff
    def __unpack__(self, context: _ContextLike) -> Optional[Any]:
        """Reads packed data from the given stream.

        This method returns nothing if this field is disabled and applies switch if
        additional options are configured.

        :param stream: the data stream
        :type stream: _StreamType
        :param context: the current context
        :type context: _ContextLike
        :return: the parsed data
        :rtype: Optional[Any]
        """
        stream: _StreamType = context[CTX_STREAM]
        if self.condition is not True and not self.is_enabled(context):
            # Disabled fields or context lambdas won't pack any data
            return

        # Using this inlined version of self.is_seq(), qe reduce the amount of
        # calls made to the method and save A LOT of time.
        # pylint: disable-next=protected-access
        context[CTX_SEQ] = F_SEQUENTIAL._hash_ in self.flags
        # pylint: disable-next=protected-access
        keep_pos = F_KEEP_POSITION._hash_ in self.flags
        if not callable(self.struct):  # REVISIT: maybe hardcode this
            if not keep_pos:
                fallback = stream.tell()

            # as above: we save A LOT of time inlining self.get_offset
            offset = self.offset(context) if callable(self.offset) else self.offset
            if offset >= 0:
                stream.seek(offset)

            context[CTX_FIELD] = self
            # Switch is applicable AFTER we parsed the first value
            try:
                value = self.struct.__unpack__(context)
                if not keep_pos:
                    stream.seek(fallback)
            # pylint: disable-next=broad-exception-caught
            except Exception as exc:
                if not isinstance(exc, StructException):
                    exc = StructException(str(exc), context)
                # Any exception leads to a default value if configured
                value = self.default
                if value == INVALID_DEFAULT or isinstance(exc, ValidationError):
                    raise exc
        else:
            # Context functions should be executed with top priority
            value = self.struct(context)

        # unpack using switch
        if self.options is not None:
            struct: _StructLike = self.get_struct(value, context)
            # The "keep_position" flag is not applicable here. Configure a field to keep the
            # position afterward.
            context[CTX_VALUE] = value
            return struct.__unpack__(context)

        return value

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        """Writes the given object to the provided stream.

        There are several options associated with this function. First, disabled
        fields will never pack any data. Next, if an offset position is specified,
        this method will first jump to that position and then parse all data.

        If this field contains a sequential type, it will automatically iterate over
        all elements in ``obj``. The final stream position will be reset if the user
        flag ``KEEP_POSITION`` is not found.

        :param obj: the value to write
        :type obj: Any
        :param stream: the output stream
        :type stream: _StreamType
        :param context: the current context with a qualified path
        :type context: _ContextLike
        :raises TypeError: if the value is not iterable but this field is marked
                           to be sequential
        """
        # TODO: revisit code
        stream: _StreamType = context[CTX_STREAM]
        if self.condition is not True and not self.is_enabled(context):
            # Disabled fields or context lambdas won't pack any data
            return

        # as above: we save A LOT of time inlining self.get_offset
        offset = self.offset(context) if callable(self.offset) else self.offset
        # pylint: disable-next=protected-access
        keep_pos = F_KEEP_POSITION._hash_ in self.flags

        context[CTX_FIELD] = self
        # pylint: disable-next=protected-access
        context[CTX_SEQ] = F_SEQUENTIAL._hash_ in self.flags
        has_offset = offset >= 0
        if not keep_pos or has_offset:
            fallback = stream.tell()

        if has_offset:
            # TODO: implement F_OFFSET_OVERRIDE
            # We write the current field into a temporary memory buffer
            # and add it after all processing hasbeen finished.
            base_stream = stream
            stream = BytesIO()
            context[CTX_STREAM] = stream

        is_lambda = callable(self.struct)
        if self.options is None and not is_lambda:
            self.struct.__pack__(obj, context)
        else:
            if not is_lambda:
                raise StructException(
                    "Attepmt was made to use switch without context lambda!", context
                )
            value = self.struct(context)
            if self.options is not None:
                struct: _StructLike = self.get_struct(value, context)
                struct.__pack__(obj, context)

        if not has_offset and not keep_pos:
            # The position shouldn't be persisted reset the stream
            stream.seek(fallback)

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
        context[CTX_SEQ] = self.is_seq()

        # 3. We should gather the element count if this field stores
        # a sequential element
        count = 1
        if context[CTX_SEQ]:
            count = self.length(context)
            if isinstance(count, _GreedyType):
                raise DynamicSizeError(
                    "Greedy field does not have a fixed size!", context
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
    def __str__(self) -> str:
        name = self.get_name() or "<unnamed>"
        offset = f", offset={self.offset}" if self.offset != -1 else ""
        return (
            f"Field({name!r}, arch={self.arch.name!r}, order={self.order.name!r}, "
            f"seq={self.is_seq()}, struct={self.struct!r}, cond={self.condition is not True}, "
            f"options={bool(self.options)}{offset})"
        )

    def __repr__(self) -> str:
        return self.__str__()


# --- private type converter ---
@registry.TypeConverter(_StructLike)
def _type_converter(annotation: _StructLike, kwargs: dict) -> Field:
    # REVISIT: more options ?
    arch = kwargs.pop("arch", None)
    order = kwargs.pop("order", None)
    return Field(annotation, order=order, arch=arch)


registry.annotation_registry.append(_type_converter)


class _CallableTypeConverter(registry.TypeConverter):
    def matches(self, annotation: Any) -> bool:
        # must be a callable but not a type
        return callable(annotation) and not isinstance(annotation, type)

    def convert(self, annotation: Any, kwargs: dict) -> _StructLike:
        arch = kwargs.pop("arch", None)
        order = kwargs.pop("order", None)
        # callables are treates as context lambdas
        return Field(annotation, order=order, arch=arch)


registry.annotation_registry.append(_CallableTypeConverter())
