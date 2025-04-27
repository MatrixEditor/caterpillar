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
import struct as PyStruct
import warnings

from io import BytesIO
from typing import Sequence, Any, Optional, Union, List, Callable
from types import EllipsisType, NoneType
from functools import cached_property
from enum import Enum as _EnumType
from uuid import UUID

from caterpillar.abc import (
    _StructLike,
    _ContextLambda,
    getstruct,
    _EnumLike,
    _StreamType,
    _ContextLike,
)
from caterpillar.exception import (
    ValidationError,
    InvalidValueError,
    DynamicSizeError,
)
from caterpillar.context import CTX_FIELD, CTX_STREAM, CTX_SEQ
from caterpillar.options import Flag, GLOBAL_FIELD_FLAGS
from caterpillar.byteorder import LittleEndian
from caterpillar import registry
from caterpillar._common import WithoutContextVar

from ._base import Field, INVALID_DEFAULT, singleton
from ._mixin import FieldStruct

# Explicitly report deprecation warnings
warnings.filterwarnings("default", category=DeprecationWarning, module=__name__)

ENUM_STRICT = Flag("enum.strict")


class PyStructFormattedField(FieldStruct):
    """
    A field class representing a binary format using format characters (e.g., 'i', 'x', etc.).

    This class allows you to define fields for binary struct formats using format characters,
    which are often used in Python's `struct` module. Each field is associated with a format character
    (like 'x' for padding or 'i' for a signed integer), and it determines how data is packed and unpacked.

    Example usage:

    >>> field = PyStructFormattedField('i', int)
    >>> field.__repr__()
    "<PyStructFormattedField(int) 'i' 32>"

    :param ch: The format character (e.g., 'i', 'x', 'f') that defines how the field is packed and unpacked.
    :param type_: The Python type that corresponds to the format character.
    """

    __slots__ = {
        "text": """The format char (e.g. 'x', 'i', ...)""",
        "ty": """The returned Python type""",
        "_padding_": """Internal field that indicates this struct is padding""",
    }

    def __init__(self, ch: str, type_: type) -> None:
        self.text = ch
        self.ty = type_
        self.__bits__ = PyStruct.calcsize(self.text) * 8
        self._padding_ = self.text == "x"

    def __fmt__(self) -> str:
        """
        Get the format character for this field.

        :return: The format character (e.g., 'i', 'x').
        :rtype: str
        """
        return self.text

    def __repr__(self) -> str:
        """
        String representation of the FormatField.

        :return: A string representation.
        """
        type_repr = self.ty.__name__ if not self._padding_ else "padding"
        return f"<{self.__class__.__name__}({type_repr}) {self.text!r} {self.__bits__}>"

    def __type__(self) -> type:
        """
        Get the Python type associated with the format specifier.

        :return: The Python type (e.g., `int`, `float`, etc.).
        :rtype: type
        """
        return self.ty

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the field in bytes.

        The size is calculated by dividing the bit size by 8 (since 1 byte = 8 bits).

        :param context: The context for the current field (can be used for calculating dynamic sizes).
        :return: The size of the field in bytes.
        :rtype: int
        """
        return self.__bits__ // 8

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single value into the stream using the defined format character.

        :param obj: The value to pack (can be of the type defined by the format character).
        :param context: The context that provides the stream and field-specific information.
        """
        if obj is None and not self._padding_:
            return  # Skip packing if the value is None and the field is not padding

        len_ = self.get_length(context)
        fmt = f"{context[CTX_FIELD].order.ch}{len_}{self.text}"
        if self._padding_:
            data = PyStruct.pack(fmt)
        elif len_ > 1:
            # Unfortunately, we have to use the *unpack operation here
            data = PyStruct.pack(fmt, *obj)
        else:
            data = PyStruct.pack(fmt, obj)
        context[CTX_STREAM].write(data)

    def pack_seq(self, seq: Sequence, context: _ContextLike) -> None:
        """
        Pack a sequence of values into the stream.

        If the context specifies a fixed amount, it will pack the sequence accordingly.

        :param seq: The sequence of values to pack.
        :param context: The context providing packing information.
        """
        if context[CTX_FIELD].amount is not Ellipsis:
            self.pack_single(seq, context)
        else:
            super().pack_seq(seq, context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single value from the stream.

        :param context: The context that provides the stream and field-specific information.
        :return: The unpacked value, converted to the field's corresponding Python type.
        """
        len_ = self.get_length(context)
        size = (self.__bits__ // 8) * len_
        value = PyStruct.unpack(
            f"{context[CTX_FIELD].order.ch}{len_}{self.text}",
            context[CTX_STREAM].read(size),
        )
        return value[0] if value else None

    def unpack_seq(self, context: _ContextLike) -> List[Any]:
        """
        Unpack a sequence of values from the stream.

        :param context: The context that provides the stream and field-specific information.
        :return: A list of unpacked values.
        """
        # We don't want to call .length() here as it would
        # consume extra time
        field = context[CTX_FIELD]
        length = field.length(context)
        if length == 0:
            return []  # maybe add factory

        if length is Ellipsis:
            return super().unpack_seq(context)

        # REVISIT:
        fmt = f"{field.order.ch}{length}{self.text}"
        size = (self.__bits__ // 8) * length
        return list(PyStruct.unpack(fmt, context[CTX_STREAM].read(size)))

    def get_length(self, context: _ContextLike) -> int:
        """
        Get the length of the field, which may be dynamically determined based on the context.

        :param context: The context providing the length information.
        :return: The length of the field (1 if no length is specified).
        :rtype: int
        """
        dim = context[CTX_FIELD].length(context)
        if dim is Ellipsis or not context[CTX_SEQ]:
            dim = 1
        return dim

    def is_padding(self) -> bool:
        """
        Check if the field represents padding.

        :return: True if the field is padding (i.e., 'x' format character), False otherwise.
        :rtype: bool
        """
        return self._padding_


# Instances of FormatField with specific format specifiers
padding = PyStructFormattedField("x", NoneType)
char = PyStructFormattedField("c", str)
boolean = PyStructFormattedField("?", bool)

int8 = PyStructFormattedField("b", int)
uint8 = PyStructFormattedField("B", int)
int16 = PyStructFormattedField("h", int)
uint16 = PyStructFormattedField("H", int)
int32 = PyStructFormattedField("i", int)
uint32 = PyStructFormattedField("I", int)
int64 = PyStructFormattedField("q", int)
uint64 = PyStructFormattedField("Q", int)


ssize_t = PyStructFormattedField("n", int)
size_t = PyStructFormattedField("N", int)

float16 = PyStructFormattedField("e", float)
float32 = PyStructFormattedField("f", float)
float64 = PyStructFormattedField("d", float)
double = float64

void_ptr = PyStructFormattedField("P", int)

_ConstType = Union[str, bytes, Any]


class Transformer(FieldStruct):
    """
    A class that acts as a transformer for encoding and decoding data using a wrapped _StructLike object.
    """

    __slots__ = ("struct",)

    def __init__(self, struct: _StructLike) -> None:
        self.struct = struct
        self.__bits__ = getattr(self.struct, "__bits__", None)

    # TODO: document this
    def __fmt__(self) -> str:
        return self.struct.__fmt__()

    def __type__(self) -> type:
        """
        Get the type of the data encoded/decoded by the transformer.

        :return: The type of the data.
        """
        return self.struct.__type__()

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the data encoded/decoded by the transformer.

        :param context: The current context.
        :return: The size of the data.
        """
        return self.struct.__size__(context)

    def encode(self, obj: Any, context: _ContextLike) -> Any:
        """
        Encode data using the wrapped _StructLike object.

        :param obj: The original data to be encoded.
        :param context: The current context.
        :return: The encoded data.
        """
        return obj

    def decode(self, parsed: Any, context: _ContextLike) -> Any:
        """
        Decode data using the wrapped _StructLike object.

        :param parsed: The parsed data to be decoded.
        :param context: The current context.
        :return: The decoded data.
        """
        return parsed

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single value into the stream using encoding.

        :param obj: The original data to be encoded and packed.
        :param context: The current context.
        """
        value = self.encode(obj, context)
        self.struct.__pack__(value, context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single value from the stream and decode it.

        :param context: The current context.
        :return: The decoded data.
        """
        value = self.struct.__unpack__(context)
        return self.decode(value, context)


class Const(Transformer):
    """
    A specialized Transformer that enforces a constant value during
    encoding and decoding.

    This class ensures that the encoded value is always the same
    constant, and when decoding, it checks if the value matches the
    expected constant. If the value doesn't match, a `ValidationError`
    is raised.

    Example usage:

    >>> # Define a constant value to enforce during encoding/decoding
    >>> const_value = 42
    >>> struct = SomeStruct() # must parse 'const_value`
    >>> field = Const(const_value, struct)
    >>> pack(None, field)
    b"\\x2a"
    >>> unpack(field, b"\\x2a")
    42

    :param value: The constant value to be enforced during encoding and decoding.
    :param struct: The _StructLike object to be wrapped.
    """

    __slots__ = ("value",)

    def __init__(self, value: _ConstType, struct: _StructLike) -> None:
        super().__init__(struct)
        self.value = value

    def encode(self, obj: Any, context: _ContextLike) -> Any:
        """
        Encode data using the constant value. This method will always return
        the constant value, regardless of the input. Therefore, :code:`None`
        can be passed as the `obj` parameter.

        :param obj: The original data to be encoded (ignored in this transformer).
        :param context: The current context (optional, not used in this implementation).
        :return: The constant value.

        Example:
            >>> constant_value = 42
            >>> transformer = Const(constant_value, SomeStruct())
            >>> transformer.encode(None, context) # context is optional
            42
        """
        return self.value

    def decode(self, parsed: Any, context: _ContextLike) -> Any:
        """
        Decode data and ensure it matches the constant value. If the
        parsed value doesn't match, a `ValidationError` is raised.

        :param parsed: The parsed data to be decoded (must match the constant value).
        :param context: The current context (optional, not used in this implementation).
        :return: The constant value if parsed matches the expected constant.
        :raises ValidationError: If the parsed value does not match the constant value.

        Example:
        >>> constant_value = 42
        >>> field = Const(constant_value, SomeStruct())
        >>> unpack(field, b"\\x2a")
        42
        >>> unpack(field, b"\\x24")
        Traceback (most recent call last):
        ...
        ValidationError: Expected 42, got 36
        """
        if parsed != self.value:
            raise ValidationError(f"Expected {self.value!r}, got {parsed!r}", context)
        return self.value


class Enum(Transformer):
    """
    A specialized Transformer for encoding and decoding enumeration values.

    This class is used for transforming between enumeration values and their corresponding
    encoded representations (typically integers). It provides encoding and decoding methods
    to ensure that enum values are serialized and deserialized correctly. Additionally, it supports
    a default value in case an invalid or unrecognized value is encountered during decoding.

    Example usage:

    >>> from enum import Enum as PyEnum
    >>> class Color(PyEnum):
    ...     RED = 1
    ...     GREEN = 2
    ...     BLUE = 3
    ...
    >>> cp_enum = Enum(Color, uint8)
    >>> pack(Color.RED, cp_enum, as_field=True)
    b"\\x01"
    >>> unpack(cp_enum, b"\\x01", as_field=True)
    Color.RED

    :param model: The enumeration model (an object with `_member_map_` and `_value2member_map_` attributes).
    :param struct: The _StructLike object to be wrapped.
    :param default: The default value to return if decoding encounters an unrecognized value.
                    Default is `INVALID_DEFAULT`.
    """

    __slots__ = ("model", "default")

    def __init__(
        self,
        model: type,
        struct: _StructLike,
        default: Optional[_EnumLike | Any] = INVALID_DEFAULT,
    ) -> None:
        super().__init__(struct)
        self.model = model
        self.default = default

    def __type__(self) -> type:
        """
        Determine the type for this transformation, which is either the enum type
        or a union of the enum and struct types, depending on the global field flags.

        :return: The type (either the enum model or a union of enum and struct types).
        """
        # pylint: disable-next=protected-access
        if ENUM_STRICT._hash_ in GLOBAL_FIELD_FLAGS:
            return self.model

        return Union[self.model, self.struct.__type__()]

    def encode(self, obj: Any, context: _ContextLike) -> Any:
        """
        Encode an enumeration value into its corresponding encoded representation.

        :param obj: The original enumeration value to encode (e.g., `Color.RED`).
        :param context: The current context.
        :return: The encoded value (usually an integer representing the enum).
        :raises ValidationError: If the input value is not a valid enum type.

        Example:
        >>> cp_enum.encode(Color.GREEN, context)
        2 # (the integer value of Color.GREEN)
        """
        if not isinstance(obj, _EnumType):
            # pylint: disable-next=protected-access
            if ENUM_STRICT._hash_ in context[CTX_FIELD].flags:
                raise ValidationError(f"Expected enum type, got {type(obj)}", context)
            return obj

        return obj.value

    def decode(self, parsed: Any, context: _ContextLike) -> Any:
        """
        Decode an encoded value (typically an integer) back to its corresponding
        enumeration value.

        :param parsed: The parsed value (usually an integer).
        :param context: The current context.
        :return: The corresponding enumeration value.
        :raises InvalidValueError: If the parsed value cannot be mapped to a valid enum.

        Example:
        >>> cp_enum.decode(1, context)
        Color.RED
        >>> unpack(1, cp_enum, as_field=True)
        Color.RED
        """
        # pylint: disable-next=protected-access
        by_name = self.model._member_map_.get(parsed)
        if by_name is not None:
            return by_name

        # pylint: disable-next=protected-access
        by_value = self.model._value2member_map_.get(parsed)
        if by_value is not None:
            return by_value

        default = self.default
        if default == INVALID_DEFAULT:
            default = context[CTX_FIELD].default

        if default == INVALID_DEFAULT:
            # pylint: disable-next=protected-access
            if ENUM_STRICT._hash_ in context[CTX_FIELD].flags:
                raise InvalidValueError(
                    f"Could not find enum for value {parsed!r}", context
                )
            return parsed
        return default


class _EnumTypeConverter(registry.TypeConverter):
    def matches(self, annotation: Any) -> bool:
        return isinstance(annotation, type) and issubclass(annotation, _EnumType)

    def convert(self, annotation: Any, kwargs: dict) -> _StructLike:
        struct_obj = getstruct(annotation)
        if not struct_obj:
            raise ValidationError(
                f"Could not infer Enum struct: could not find __struct__ attribute on annotation {annotation!r}"
            )
        return Enum(annotation, struct_obj)


# TODO: document why this has to be at first position
registry.annotation_registry.insert(0, _EnumTypeConverter())


class Memory(FieldStruct):
    """
    A class representing a memory field that handles packing and unpacking byte-like objects
    of a specified length.

    The `Memory` class is used to manage fields that contain raw byte data. It allows you to
    pack a byte object (either `bytes` or `memoryview`) into a stream and unpack byte data
    from a stream into a `memoryview`. The length of the memory field can be fixed or dynamically
    determined based on the context. If the length is unspecified, the entire available data in
    the stream is read.

    This class can handle the following scenarios for the `length` argument:
    - **Fixed length**: A specific number of bytes (e.g., `10`).
    - **Dynamic length**: A callable that returns the length based on the current context (e.g., `lambda ctx: ctx["length"]`).
    - **Greedy length**: Using `Ellipsis` (`...`), meaning the entire stream is read regardless of the size.

    Examples:

    >>> # Memory with a fixed length of 10 bytes
    >>> memory = Memory(10)
    >>> memory_dynamic = Memory(lambda ctx: ctx._root.length) # dynamic length based on context
    >>> memory_greedy = Memory(...)
    >>> pack(b"1234567890", memory, as_field=True)
    b"1234567890"
    >>> pack(b"1234567890", memory_dynamic, as_field=True, length=10)
    b"1234567890"
    >>> unpack(b"1234567890", memory_greedy, as_field=True)
    b"1234567890"

    :param length: The length of the memory to pack or unpack. It can be:
                   - An integer specifying the number of bytes to handle.
                   - A callable that dynamically returns the number of bytes based on the context.
                   - Ellipsis (`...`), indicating the length is unspecified and the entire stream should be read.
    """

    __slots__ = ("length",)

    def __init__(
        self,
        length: Union[int, _ContextLambda, EllipsisType],
    ) -> None:
        self.length = length

    def __type__(self) -> type:
        """
        Return the type of the field, which is `memoryview` for this class.

        :return: `memoryview`
        """
        return memoryview

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the memory field based on the `length` parameter.

        If the `length` is callable, it will be invoked with the context to get the size.
        If the `length` is `Ellipsis`, the size is unspecified and the entire stream will be read.

        :param context: The current context.
        :return: The size of the field in bytes, or `Ellipsis` if the length is unspecified.
        """
        return self.length(context) if callable(self.length) else self.length

    def pack_single(self, obj: Union[memoryview, bytes], context: _ContextLike) -> None:
        """
        Pack a single byte object (memoryview or bytes) into the stream.

        This method writes a byte object (`memoryview` or `bytes`) into the stream,
        ensuring that the size of the object matches the expected length defined by
        the `Memory` field. If the expected size is fixed (not `Ellipsis`), a
        validation is performed to ensure that the length of the `obj` matches
        the expected size.

        Examples:

        >>> memory = Memory(10)
        >>> pack(b"1234567890", memory, as_field=True) # Packs exactly 10 bytes into the stream
        b"1234567890"
        >>> pack(b"1", memory, as_field=True)
        Traceback (most recent call last):
        ...
        ValidationError: Memory field expected 10 bytes, but got 1 bytes instead

        :param obj: The byte object to be packed. This can be either a `memoryview` or a `bytes` object.
        :param context: The current context, which provides access to the stream and any additional metadata needed
                        for packing.

        :raises ValidationError: If the length of the `obj` does not match the expected size.
        """
        size = self.__size__(context)
        if size is not Ellipsis:
            if len(obj) != size:
                raise ValidationError(
                    f"Memory field expected {size} bytes, but got {len(obj)} bytes instead",
                    context,
                )
        context[CTX_STREAM].write(obj)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single byte object (memoryview) from the stream.

        This method reads bytes from the stream into a `memoryview`. The size
        of the object to be unpacked is determined by the `Memory` field's length.
        If the length is fixed (not `Ellipsis`), it reads exactly that number of
        bytes. If the length is unspecified (i.e., `Ellipsis`), it reads until the
        end of the stream.

        :param context: The current context, which provides access to the stream and
                        any additional metadata needed for unpacking.
        :return: A `memoryview` object representing the unpacked byte data.
        """
        stream: _StreamType = context[CTX_STREAM]
        size = self.__size__(context)
        return memoryview(stream.read(size) if size is not Ellipsis else stream.read())


class Bytes(Memory):
    """Byte sequences.

    Same class as :class:`Memory` but with a type of `bytes` instead of `memoryview`.
    """

    __slots__ = ()

    def __type__(self) -> type:
        """
        Return the type associated with this `Bytes` field, which is `bytes`.

        :return: The type (bytes).
        """
        return bytes

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single byte sequence (bytes) from the stream.

        :param context: The current context, which provides access to the stream and
                        other necessary metadata for unpacking.
        :return: A `bytes` object representing the unpacked data from the stream.

        """
        # as we read bytes from the stream, this will return a bytes object
        return super().unpack_single(context).obj


class String(Memory):
    """String sequences.

    Same class as :class:`Memory` but with a type of `str` instead of `memoryview`.

    :param length: The length of the string to pack or unpack. It can be:
                   - An integer specifying the number of bytes (e.g., `10`).
                   - A callable that dynamically returns the number of bytes based on the context (e.g., `lambda ctx: ctx["length"]`).
                   - Ellipsis (`...`), meaning the entire available stream should be read, regardless of size.
    :param encoding: The encoding to use for converting bytes to a string during unpacking. If not specified, defaults to `None`.
                     If specified, the string will be decoded using this encoding (e.g., `utf-8`).
    """

    __slots__ = ("encoding",)

    def __init__(
        self,
        length: Union[int, _ContextLambda, EllipsisType],
        encoding: Optional[str] = None,
    ) -> None:
        super().__init__(length)
        self.encoding = encoding or "utf-8"

    def __type__(self) -> type:
        """
        Return the type associated with this `String` field.

        :return: `str` - the type associated with the `String` field.
        """
        return str

    def pack_single(self, obj: str, context: _ContextLike) -> None:
        """Packs a single string into the stream."""
        return super().pack_single(obj.encode(self.encoding), context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single string from the stream.

        :param context: The current context.
        :return: A `str` representing the unpacked string, decoded from bytes using the specified encoding.
        """
        return super().unpack_single(context).obj.decode(self.encoding)


class CString(FieldStruct):
    """
    C-style strings (null-terminated or padded).

    This class is designed for handling strings that are padded to a
    fixed length, typically with zero-padding or any custom padding
    character. It is useful for encoding and decoding data that follows
    the C-style string conventions, where strings are often represented
    by a fixed length, and padding (e.g., null bytes) is used to fill
    the remaining space.

    Example usage:

    >>> cstring = CString(10, encoding='utf-8') # encoding is optional
    >>> pack(cstring, "Hello, World!")
    b"Hello, World\\x00"
    >>> unpack(cstring, b"Hello, World\\x00")
    'Hello, World!'

    This class also supports direct getitem access to create a list:

    >>> cstrings = CString[10] # array of ten strings (variable size)

    :param length: The fixed length of the C-string or a callable that determines
                   the length based on the context. If `None` or `Ellipsis`, the
                   string will be unpacked until the padding character is found.
    :param encoding: The encoding to use for converting the byte data to a string.
                    Defaults to `utf-8`. If `None`, the default encoding is used.
    :param pad: The padding character to use (usually `0` for null padding). If a
                string is provided, it must be a single character. If not specified,
                defaults to `0` (null byte).
    """

    __slots__ = ("encoding", "pad", "_raw_pad")

    def __init__(
        self,
        length: Union[int, _ContextLambda, None, EllipsisType] = None,
        encoding: Optional[str] = None,
        pad: Union[str, int, None] = None,
    ) -> None:
        """
        Initialize the String field with a fixed length or a length determined by a context lambda.

        :param length: The fixed length or a context lambda to determine the length dynamically.
        :param encoding: The encoding to use for string encoding/decoding (default is UTF-8).
        """
        self.length = length or ...
        self.encoding = encoding or "utf-8"
        self.pad = pad or 0
        if isinstance(self.pad, str):
            if len(self.pad) != 1:
                raise ValueError(
                    f"Invalid padding {pad!r}. Padding must be a single character."
                )
            self.pad = ord(self.pad)

        if not isinstance(self.pad, int):
            raise ValueError(
                f"Invalid padding {pad!r}. Padding must be a an integer or a single character."
            )
        self._raw_pad = self.pad.to_bytes(1)

    def __class_getitem__(cls, dim) -> Field:
        """
        Allows indexing for `CString` class to support field dimensioning.

        :param dim: The dimension or index of the field.
        :return: A new instance of `CString` with the specified dimension.
        """
        return CString(...)[dim]

    def __size__(self, context: _ContextLike) -> Any:
        """
        Returns the size of the `CString` field.

        :param context: The context used to determine the size.
        :return: The length of the field in bytes.
        """
        return self.length(context) if callable(self.length) else self.length

    def __type__(self) -> type:
        """
        Returns the type associated with the `CString` field.

        :return: The `str` type, as the field stores string data.
        """
        return str

    def pack_single(self, obj: str, context: _ContextLike) -> None:
        """
        Pack a single string into the stream with padding.

        This method encodes the string into bytes and pads it to the
        fixed length, if applicable. If the length is dynamic or
        unspecified, padding is added until the total length is achieved.

        :param obj: The string to pack into the stream.
        :param context: The current context.
        :raises ValidationError: If the string is too long for the fixed length.
        """
        encoded = obj.encode(self.encoding)
        stream = context[CTX_STREAM]
        if self.length is not Ellipsis:
            length = self.__size__(context)
            obj_length = len(obj)
            if obj_length > length:
                raise ValidationError(
                    f"String {obj!r} is too long for the fixed length of {length} bytes."
                )
            stream.write(encoded)
            stream.write(self._raw_pad * (length - obj_length))
        else:
            stream.write(encoded)
            stream.write(self._raw_pad)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single C-style string from the stream.

        This method reads bytes from the stream until a padding
        character is found. If the length is fixed, it will unpack
        exactly that number of bytes. If length is unspecified, it
        unpacks until the padding character is encountered.

        :param context: The current context, which provides access to the
                        stream and other necessary metadata.
        :return: The unpacked string, stripped of padding, decoded with
                 the specified encoding.
        """
        if self.length is Ellipsis:
            # Parse actual C-String
            stream = context[CTX_STREAM]
            data = bytearray()
            while True:
                value = stream.read(1)
                if not value or value[0] == self._raw_pad[0]:
                    break
                data.extend(value)
            value = bytes(data)
        else:
            length = self.__size__(context)
            value: bytes = context[CTX_STREAM].read(length)

        return value.rstrip(self._raw_pad).decode(self.encoding)


class ConstString(Const):
    """
    A specialized constant field for handling fixed string values.

    This class is used to define a field that always holds a constant
    string value. The value is validated during both encoding and
    decoding to ensure that the expected constant string is preserved.
    The string can optionally be encoded in a specific encoding.

    Additionally, this class provides a type converter that can be used
    to convert a string annotation to a `ConstString` field.

    >>> @struct
    ... class MyStruct:
    ...     value: "const str" # <-- will be converted to ConstString

    Note that the type declaration above won't work if you enable
    annotation evaluation.

    Examples:

    >>> # Define a constant string value to enforce during encoding/decoding
    >>> const_str = ConstString("Hello, World!")
    >>> pack(None, const_str, as_field=True)
    b"Hello, World!"
    >>> unpack(const_str, b"Hello, World!", as_field=True)
    "Hello, World!"

    :param value: The constant string value to be encoded/decoded.
    :param encoding: The encoding to use for the string (default is UTF-8).
                     If `None`, the default system encoding is used.
    """

    __slots__ = ()

    def __init__(self, value: str, encoding: Optional[str] = None) -> None:
        if not isinstance(value, str):
            raise TypeError("value must be a string")

        struct = String(len(value), encoding)
        super().__init__(value, struct)
        # REVISIT: rework bitfield
        self.__bits__ = len(value) * 8


@registry.TypeConverter(str)
def _str_type_converter(annotation: str, kwargs: dict) -> ConstString:
    return ConstString(annotation)


registry.annotation_registry.append(_str_type_converter)


class ConstBytes(Const):
    """
    A constant field for handling fixed bytes values.

    This class is used to define a field that always holds a constant
    bytes value. The value is validated during both encoding and
    decoding to ensure that the expected constant byte sequence is
    preserved.

    This class provides a type converter that can be used to convert
    a bytes annotation to a `ConstBytes` field.

    >>> @struct
    ... class MyStruct:
    ...     value: b"const bytes" # <-- will be converted to ConstBytes

    :param value: The constant bytes value to be encoded/decoded.
    """

    __slots__ = ()

    def __init__(self, value: bytes) -> None:
        super().__init__(value, Bytes(len(value)))
        self.__bits__ = len(value) * 8


@registry.TypeConverter(bytes)
def _bytes_type_converter(annotation: bytes, kwargs: dict) -> ConstBytes:
    return ConstBytes(annotation)


registry.annotation_registry.append(_bytes_type_converter)


class Computed(FieldStruct):
    """
    A specialized field for representing computed or dynamically calculated values.

    This class is used to define a field that holds a computed value. The value
    can either be a constant or a function (lambda) that computes the value
    dynamically based on the context during packing or unpacking.

    The computed value is not directly stored; instead, it is evaluated using
    the provided lambda function or constant value during encoding and decoding.

    Examples:

    >>> # Define a computed field with a constant value
    >>> computed = Computed(42)
    >>> unpack(computed, b"\\x00\\x01", as_field=True)
    42
    >>> pack(None, computed, as_field=True)
    b"" # won't affect the stream

    :param value: A constant value or a lambda function that computes the value
                  based on the context.
    """

    __slots__ = ("value",)

    def __init__(self, value: Union[_ConstType, _ContextLambda]) -> None:
        self.value = value
        self.__bits__ = 0

    def __type__(self) -> type:
        """
        Return the type of the computed field.

        :return: `Any` if callable, otherwise the type of the constant value.
        """
        return Any if callable(self.value) else type(self.value)

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        """
        No packing is needed for computed fields, as the value is computed dynamically.

        This function exists to satisfy the `FieldStruct` interface, but does not
        perform any packing.

        :param obj: The object to pack.
        :param context: The current context.
        """
        pass

    def __size__(self, context: _ContextLike) -> int:
        """
        Return the size of the computed field.

        Since the field is computed dynamically, the size is fixed as `0`.

        :param context: The current context.
        :return: Always returns `0` for computed fields.
        """
        return 0

    def __unpack__(self, context: _ContextLike) -> Any:
        """
        Unpack the computed value based on the context.

        If the value is a callable (lambda), it will be invoked with the context
        to calculate the value. Otherwise, the constant value is returned directly.

        :param context: The current context.
        :return: The computed value or the constant value.
        """
        return self.value(context) if callable(self.value) else self.value

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        No packing is needed for computed fields.

        :param obj: The object to pack.
        :param context: The current context.
        """
        # No need for an implementation
        pass

    def unpack_single(self, context: _ContextLike) -> None:
        """
        No unpacking is needed for computed fields.

        :param context: The current context.
        """
        # No need for an implementation
        pass


@singleton
class Pass(FieldStruct):
    """
    A specialized field that does nothing during packing and unpacking.

    This class is used to define a field that effectively "passes" through
    the packing and unpacking process without any modifications or
    transformations. It serves as a placeholder that doesn't store or process
    any data. This can be useful in cases where you need a field in a structure
    but don't want it to affect the overall packing or unpacking logic.

    The `Pass` field always returns `None` during unpacking and does not
    perform any operations during packing.

    Example usage:

    >>> @struct
    ... class MyStruct:
    ...     abc: Pass
    ...
    >>> obj = unpack(MyStruct, b"\\x00\\x01")
    MyStruct(abc=None)
    >>> pack(MyStruct(abc=None))
    b""
    """

    __slots__ = ()

    def __bits__(self) -> int:
        """
        Return the size in bits for the Pass field.

        Since the `Pass` field doesn't hold any data, it is considered to have a
        size of `0` bits.

        :return: Always returns `0` for the Pass field.
        """
        return 0

    def __type__(self) -> type:
        """
        Return the type associated with this Pass field.

        The `Pass` field doesn't have a type associated with actual data. It
        effectively represents a `None` type when unpacked.

        :return: `NoneType`.
        """
        return None.__class__

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        pass

    def __size__(self, context: _ContextLike) -> int:
        return 0

    def __unpack__(self, context: _ContextLike) -> Any:
        return None

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        # No need for an implementation
        pass

    def unpack_single(self, context: _ContextLike) -> None:
        # No need for an implementation
        pass


class Prefixed(FieldStruct):
    """
    A specialized field for handling data with a prefix (typically indicating length or size).

    This class is used when you want to prefix a data structure with a size or other identifying
    information. The prefix is typically packed first, followed by the actual data. The field
    allows for handling both prefixed data with a structure and simple byte sequences, depending
    on the presence of the `struct` argument. However, the returned prefix value must be
    an integer.

    Example usage:

    >>> prefixed = Prefixed(uint32, Bytes(4))
    >>> pack(b"abcd", prefixed, as_field=True)
    b"\\x00\\x00\\x00\\x04abcd"
    >>> unpack(prefixed, b"\\x00\\x00\\x00\\x04abcd", as_field=True)
    b"abcd"

    The prefix is packed and unpacked independently and is used to determine the size of the
    following data.

    **Please note that this class will have a huge impact on the resulting packing and
    unpacking time and will increase it significantly.**

    Starting from v2.4.0, this class uses the `struct` as its second parameter, moving the
    'encoding' parameter to the third parameter.

    :param prefix: The struct that defines the prefix (e.g., a length field).
    :param struct: The struct that defines the data to follow the prefix (e.g., `Bytes` or another field).
    :param encoding: The encoding to use for the prefix.
    """

    __slots__ = ("prefix", "struct", "encoding")

    def __init__(
        self,
        prefix: _StructLike,
        struct: Optional[_StructLike] = None,
        encoding: Optional[str] = None,
    ):
        self.prefix = prefix
        self.struct = struct
        self.encoding = encoding
        # Support str as second argument
        if isinstance(struct, str):
            warnings.warn(
                "Using a string as the second argument is deprecated since 2.4.0. Please use encoding=... instead!",
                DeprecationWarning,
            )
            self.encoding, self.struct = struct, None

    def __type__(self) -> Optional[Union[type, str]]:
        """
        Return the type associated with this Prefixed field.

        If the `struct` is provided, it returns the type of the `struct`. Otherwise, it returns
        `bytes` as the default type for a prefixed field.

        :return: The type associated with the Prefixed field (`bytes` or the type of the struct).
        """
        return bytes if self.struct is None else self.struct.__type__()

    def __size__(self, context: _ContextLike) -> int:
        """
        Prefixed fields do not have a fixed size.

        The size of a `Prefixed` field is dynamic, as it depends on the prefix and the data length,
        which can vary. Therefore, calling this method will raise an error.

        :raises DynamicSizeError: Always raises an error as the size is not fixed.
        """
        raise DynamicSizeError("Prefixed does not store a size", context)

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single object into the stream, with the prefix indicating the size.

        This method first packs the length of the data (the prefix), and then writes the actual data.

        :param obj: The object to pack (should be a byte sequence).
        :param context: The current context.
        """
        # REVISIT: We can only provide a value with __len__ here
        if self.struct is not None:
            data = BytesIO()
            with WithoutContextVar(context, CTX_STREAM, data):
                self.struct.__pack__(obj, context)

            obj = data.getvalue()

        elif self.encoding:
            obj = obj.encode(self.encoding)

        self.prefix.__pack__(len(obj), context)
        context[CTX_STREAM].write(obj)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single object from the stream, using the prefix to determine the size.

        This method first unpacks the prefix (which indicates the size), then reads the data
        from the stream based on that size. If a `struct` is provided, the data is then passed
        through the specified structure for further unpacking.

        :param context: The current context.
        :return: The unpacked object, which is either raw bytes or the data structure.
        """
        size = self.prefix.__unpack__(context)
        if not isinstance(size, int):
            raise TypeError(f"Expected int, got {type(size)}")

        data = context[CTX_STREAM].read(size)
        obj = data
        if self.struct is not None:
            with (
                WithoutContextVar(context, CTX_STREAM, BytesIO(data)),
                WithoutContextVar(context, CTX_SEQ, False),
            ):
                obj = self.struct.__unpack__(context)
        elif self.encoding:
            obj = data.decode(self.encoding)
        return obj


class Int(FieldStruct):
    """Generic Integer

    This class handles packing and unpacking integer values with a specified bit size, either
    signed or unsigned. The size of the integer is defined in bits, and the class ensures the
    appropriate byte representation is used for packing and unpacking.

    :param bits: The bit width of the integer (e.g., 8, 16, 32, 64).
    :param signed: Whether the integer is signed (default is True).
    """

    __slots__ = ("signed", "size")

    def __init__(self, bits: int, signed: bool = True) -> None:
        self.signed = signed
        self.__bits__ = bits
        if not isinstance(bits, int):
            raise ValueError(f"Invalid int size: {bits!r} - expected int")
        self.size = self.__bits__ // 8

    def __type__(self) -> type:
        """
        Return the type associated with this Int field.

        :return: The type of the field, which is `int`.
        """
        return int

    def __size__(self, context: _ContextLike) -> int:
        """
        Return the size of the integer in bytes.

        :param context: The current context.
        :return: The size of the integer in bytes.
        """
        return self.size

    def pack_single(self, obj: int, context: _ContextLike) -> None:
        """
        Pack a single integer value into the stream.

        This method converts the integer value into a byte representation using the specified
        byte order. The byte order is determined from the context's field order
        (either little-endian or big-endian).

        :param obj: The integer value to pack.
        :param context: The current context, which provides the byte order (little-endian or big-endian).
        :raises ValueError: If the integer is too large or small for the given bit width.
        """
        order = context[CTX_FIELD].order
        byteorder = "little" if order is LittleEndian else "big"
        context[CTX_STREAM].write(
            obj.to_bytes(self.size, byteorder, signed=self.signed)
        )

    def unpack_single(self, context: _ContextLike) -> int:
        """
        Unpack a single integer value from the stream.

        This method reads a byte sequence from the stream, interprets it as an integer using the
        specified byte order and signedness, and returns the integer value.

        :param context: The current context, which provides the byte order (little-endian or big-endian).
        :return: The unpacked integer value.
        :raises ValueError: If the data cannot be unpacked as an integer of the specified size.
        """
        order = context[CTX_FIELD].order
        byteorder = "little" if order is LittleEndian else "big"
        return int.from_bytes(
            context[CTX_STREAM].read(self.size), byteorder, signed=self.signed
        )


class UInt(Int):
    """Generic unsigned integer."""

    __slots__ = ()

    def __init__(self, bits: int) -> None:
        super().__init__(bits, signed=False)


int24 = Int(24)
uint24 = UInt(24)


class Aligned(FieldStruct):
    """
    Alignment of a struct (before or after)

    This class ensures that the associated `struct` is properly aligned according to
    the specified alignment. It allows for padding before or after the field, ensuring
    that the field starts or ends at a memory address that is a multiple of the alignment.

    Example usage:

    >>> @struct
    ... class Format:
    ...     a: Aligned(int16, alignment=4, after=True)
    ...     b: uint8
    ...
    >>> unpack(Format, b"\\x00\\x01\\xFF\\xFF\\x01")
    Traceback (most recent call last):
    ...
    ValueError: Expected 2 bytes of padding (value=0), got 0
    >>> unpack(Format, b"\\x00\\x01\\x00\\x00\\x01")
    Format(a=256, b=1)

    This example shows a `Format` structure where:
    - `a` is an aligned integer (with 4-byte alignment) and padding is applied after the field.
    - `b` is an unsigned byte (`uint8`), which follows `a` after the padding.

    :param struct: The structure that is to be aligned.
    :param alignment: The alignment value in bytes, which must be a power of 2.
                      This can be an integer or a context lambda for dynamic alignment.
    :param after: If `True`, padding is applied after the structure (align after).
    :param before: If `True`, padding is applied before the structure (align before).
    :param filler: The byte value to use for padding. It can be an integer or a string
                   (default is zero-padding). If no filler is provided, `b"\x00"` will
                   be used as the padding byte.
    :raises ValueError: If neither `before` nor `after` is specified, if the filler is not a
                        single byte, or if the padding does not match the expected value.
    :raises DynamicSizeError: If dynamic alignment is used and the size cannot be determined.
    """

    __slots__ = ("struct", "_after", "_before", "_filler", "alignment")

    def __init__(
        self,
        struct: _StructLike,
        alignment: Union[int, _ContextLambda],
        after: bool = False,
        before: bool = False,
        filler: Union[int, str, None] = None,
    ) -> None:
        if not before and not after:
            raise ValueError("Must specify either before or after")

        self.struct = struct
        self.alignment = alignment
        self._after = after
        self._before = before
        if filler is None:
            self._filler = 0x00
        else:
            if isinstance(filler, str):
                self._filler = ord(filler)
            else:
                self._filler = filler

        if not isinstance(self._filler, int):
            raise ValueError(f"Filler must be a single byte - got {filler!r}")

    def __type__(self) -> Optional[Union[type, str]]:
        """
        Return the type associated with this aligned field.

        :return: The type of the struct (usually `bytes` or another custom type).
        """
        return self.struct.__type__()

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the aligned field, accounting for padding based on the alignment.

        :param context: The current context.
        :return: The size of the aligned field, including padding if necessary.
        :raises DynamicSizeError: If the alignment is dynamic and cannot be determined.
        """
        if callable(self.alignment):
            raise DynamicSizeError(
                "Aligned fields with dynamic alignment don't have a fixed size"
            )

        struct_size = self.struct.__size__(context)
        return struct_size + (self.alignment - (struct_size % self.alignment))

    def unpack_alignment(self, context: _ContextLike):
        """
        Unpack padding for the alignment, verifying that the correct amount of padding is present.

        :param context: The current context.
        :raises ValueError: If the padding does not match the expected value.
        """
        value = self.alignment(context) if callable(self.alignment) else self.alignment
        if not isinstance(value, int):
            raise ValueError(f"Alignment must be an integer - got {value!r}")

        if value % 2 != 0:
            raise ValueError(f"Alignment must be a power of 2 - got {value!r}")

        stream = context[CTX_STREAM]
        pos = stream.tell()
        size = value - (pos % value)
        data = stream.read(size)
        if data.count(self._filler) != size:
            raise ValueError(
                f"Expected {size} bytes of padding (value={self._filler!r}), got {data.count(self._filler)}"
            )

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single aligned field from the stream.

        This method ensures that padding is applied before or after the field as needed
        based on the `before` and `after` parameters.

        :param context: The current context.
        :return: The unpacked structure, properly aligned.
        """
        if self._before:
            self.unpack_alignment(context)
        obj = self.struct.__unpack__(context)
        if self._after:
            self.unpack_alignment(context)
        return obj

    def pack_alignment(self, context: _ContextLike):
        """
        Apply padding for the alignment before or after the structure, depending on
        the `before` and `after` settings.

        :param context: The current context.
        """
        value = self.alignment(context) if callable(self.alignment) else self.alignment
        stream = context[CTX_STREAM]
        size = value - (stream.tell() % value)
        stream.write(bytes([self._filler] * size))

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single aligned field into the stream, applying padding if necessary.

        :param obj: The structure to pack.
        :param context: The current context.
        """
        if self._before:
            self.pack_alignment(context)
        self.struct.__pack__(obj, context)
        if self._after:
            self.pack_alignment(context)


def align(alignment: Union[int, _ContextLambda]) -> _ContextLambda:
    """
    Create a context lambda to calculate the alignment padding required at the current stream position.

    This function generates a lambda that can be used to compute the amount of padding required
    to ensure that the next structure in the stream is aligned to the specified alignment.

    The alignment value can either be a fixed integer (representing the alignment in bytes)
    or a context lambda that computes the alignment dynamically based on the current context.

    Example usage:

    >>> @struct
    ... class Format:
    ...     a: uint8
    ...     b: padding[align(4)]
    ...
    >>> unpack(Format, b"\\x01\\x00\\x00\\x00")
    Format(a=1, b=None)

    :param alignment: The alignment value in bytes, which must be a power of 2.
                      This can be either an integer or a context lambda.
    :return: A context lambda function that returns the number of bytes to align the next structure.
    """

    def _get_aligned_size(context: _ContextLike) -> Any:
        pos = context[CTX_STREAM].tell()
        value = alignment(context) if callable(alignment) else alignment
        return value - (pos % value)

    return _get_aligned_size


class Lazy(FieldStruct):
    """
    A lazy field struct that defers the creation of the underlying struct until it is needed.

    This class allows the definition of a field where the underlying struct is not created until
    the field is actually accessed. This can help with optimization in scenarios where certain
    fields may not always be used.

    The underlying struct is defined by a callable that returns an instance of a struct.
    The `struct_fn` function is invoked to generate the struct when the field is accessed.

    Example usage:

    >>> @struct
    ... class Format:
    ...     a: Lazy(lambda: SecondFormat)  # Lazy instantiation of the struct
    ...     b: uint8
    ...
    >>> @struct
    ... class SecondFormat:
    ...     a: uint8
    ...
    >>> unpack(Format, b"\\x01\\x02\\xFF")
    Format(a=SecondFormat(a=1), b=255)

    :param struct: A callable that returns the underlying struct, which will be lazily created
                   when the field is accessed.
    """

    def __init__(self, struct: Callable[[], _StructLike]) -> None:
        if not callable(struct):
            raise TypeError(f"struct must be a callable - got {struct!r}")

        self.struct_fn = struct

    @cached_property
    def struct(self) -> _StructLike:
        """
        Get the underlying struct by invoking the callable.

        This method ensures that the struct is only created once, and it is cached for subsequent use.

        :return: The underlying struct.
        :rtype: _StructLike
        """
        return self.struct_fn()

    def __bits__(self) -> str:
        """
        Get the bit representation of the Lazy struct by delegating to the underlying struct.

        :return: The bit representation of the struct.
        :rtype: str
        """
        return self.struct.__bits__()

    def __type__(self) -> type:
        """
        Get the type associated with the Lazy struct by delegating to the underlying struct.

        :return: The type associated with the struct.
        :rtype: type
        """
        return self.struct.__type__()

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the Lazy struct by delegating to the underlying struct.

        :param context: The context for size calculation.
        :return: The size of the struct.
        :rtype: int
        """
        return self.struct.__size__(context)

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single value using the Lazy struct by delegating to the underlying struct.

        :param obj: The value to pack.
        :param context: The context for packing.
        """
        self.struct.__pack__(obj, context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single value using the Lazy struct by delegating to the underlying struct.

        :param context: The context for unpacking.
        :return: The unpacked value.
        """
        return self.struct.__unpack__(context)


@singleton
class Uuid(FieldStruct):
    """
    A field for handling UUID values.

    This class is responsible for serializing and deserializing UUIDs to and
    from their binary representation. The UUID is represented as a 16-byte
    field (128 bits) and supports both little-endian and big-endian formats.

    Example usage:

    >>> unpack(Uuid, b'e3215476e89b12d3', as_field=True)
    UUID('65333231-3534-3736-6538-396231326433')

    :param value: The UUID value, which is typically a `UUID` object from the
                  `uuid` module.
    :param context: The context for packing and unpacking the UUID. The
                    context includes stream order information for byte
                    order (little-endian or big-endian).
    """

    __slots__ = ()

    def __type__(self) -> type:
        """
        Get the type associated with the UUID field.

        :return: The type `UUID`.
        :rtype: type
        """
        return UUID

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the UUID field.

        :param context: The context for size calculation.
        :return: The size of the UUID in bytes (16 bytes).
        :rtype: int
        """
        return 16

    def __bits__(self) -> int:
        """
        Get the bit representation of the UUID field.

        :return: The bit size of the UUID field (128 bits).
        :rtype: int
        """
        return 128

    def __pack__(self, obj: UUID, context: _ContextLike) -> None:
        """
        Pack a UUID object into the stream.

        Depending on the byte order (little-endian or big-endian) specified
        in the context, the UUID will be packed in the corresponding byte order.

        :param obj: The `UUID` object to pack.
        :param context: The current context, which includes the stream and byte order.
        """
        is_le = context[CTX_FIELD].order is LittleEndian
        super().__pack__(obj.bytes_le if is_le else obj.bytes, context)

    def __unpack__(self, context: _ContextLike) -> UUID:
        """
        Unpack a UUID from the stream.

        Depending on the byte order (little-endian or big-endian) specified
        in the context, the UUID will be unpacked in the corresponding byte order.

        :param context: The current context, which includes the stream and byte order.
        :return: The unpacked `UUID` object.
        :rtype: UUID
        """
        is_le = context[CTX_FIELD].order is LittleEndian
        data = context[CTX_STREAM].read(16)
        return UUID(bytes_le=data) if is_le else UUID(bytes=data)
