# Copyright (C) MatrixEditor 2023-2024
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
import struct as libstruct
import pickle

from typing import Callable, Type
from typing import Sequence, Any, Optional, Union, List
from types import EllipsisType, NoneType
from functools import cached_property
from enum import Enum as _EnumType
from uuid import UUID

from caterpillar.abc import _StructLike, _ContextLambda, getstruct
from caterpillar.abc import _EnumLike, _StreamType
from caterpillar.abc import _ContextLike

from caterpillar.exception import (
    ValidationError,
    InvalidValueError,
    DynamicSizeError,
)
from caterpillar.context import CTX_FIELD, CTX_STREAM, CTX_SEQ
from caterpillar.options import Flag, GLOBAL_FIELD_FLAGS
from caterpillar.byteorder import LittleEndian
from caterpillar import registry

from ._base import Field, INVALID_DEFAULT, singleton
from ._mixin import FieldStruct, FieldMixin


ENUM_STRICT = Flag("enum.strict")


class FormatField(FieldStruct):
    """
    A field class representing a binary format.
    """

    __slots__ = {
        "text": """The format char (e.g. 'x', 'i', ...)""",
        "ty": """The returned Python type""",
        "_padding_": """Internal field that indicates this struct is padding""",
    }

    def __init__(self, ch: str, type_: type) -> None:
        self.text = ch
        self.ty = type_
        self.__bits__ = libstruct.calcsize(self.text) * 8
        self._padding_ = self.text == "x"

    def __fmt__(self) -> str:
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

        :return: The Python type.
        """
        return self.ty

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the field (single element).

        :param context: The current context.
        :return: The size of the field.
        """
        return self.__bits__ // 8

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single value into the stream.

        :param obj: The value to pack.
        :param stream: The output stream.
        :param context: The current context.
        """
        if obj is None and not self._padding_:
            return

        len_ = self.get_length(context)
        fmt = f"{context[CTX_FIELD].order.ch}{len_}{self.text}"
        if self._padding_:
            data = libstruct.pack(fmt)
        elif len_ > 1:
            # Unfortunately, we have to use the *unpack operation here
            data = libstruct.pack(fmt, *obj)
        else:
            data = libstruct.pack(fmt, obj)
        context[CTX_STREAM].write(data)

    def pack_seq(self, seq: Sequence, context: _ContextLike) -> None:
        """
        Pack a sequence of values into the stream.

        :param seq: The sequence of values.
        :param context: The current context.
        """
        if context[CTX_FIELD].amount is not Ellipsis:
            self.pack_single(seq, context)
        else:
            super().pack_seq(seq, context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single value from the stream.

        :param context: The current context.
        :return: The unpacked value.
        """
        len_ = self.get_length(context)
        size = (self.__bits__ // 8) * len_
        value = libstruct.unpack(
            f"{context[CTX_FIELD].order.ch}{len_}{self.text}",
            context[CTX_STREAM].read(size),
        )
        return value[0] if value else None

    def unpack_seq(self, context: _ContextLike) -> List[Any]:
        """
        Unpack a sequence of values from the stream.

        :param context: The current context.
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
        return list(libstruct.unpack(fmt, context[CTX_STREAM].read(size)))

    def get_length(self, context: _ContextLike) -> int:
        dim = context[CTX_FIELD].length(context)
        if dim is Ellipsis or not context[CTX_SEQ]:
            dim = 1
        return dim

    def is_padding(self) -> bool:
        """
        Check if the field represents padding.

        :return: True if the field is padding, False otherwise.
        """
        return self._padding_


# Instances of FormatField with specific format specifiers
padding = FormatField("x", NoneType)
char = FormatField("c", str)
boolean = FormatField("?", bool)

int8 = FormatField("b", int)
uint8 = FormatField("B", int)
int16 = FormatField("h", int)
uint16 = FormatField("H", int)
int32 = FormatField("i", int)
uint32 = FormatField("I", int)
int64 = FormatField("q", int)
uint64 = FormatField("Q", int)


ssize_t = FormatField("n", int)
size_t = FormatField("N", int)

float16 = FormatField("e", float)
float32 = FormatField("f", float)
float64 = FormatField("d", float)
double = float64

void_ptr = FormatField("P", int)

_ConstType = Union[str, bytes, Any]


class Transformer(FieldStruct):
    """
    A class that acts as a transformer for encoding and decoding data using a wrapped _StructLike object.
    """

    __slots__ = ("struct",)

    def __init__(self, struct: _StructLike) -> None:
        self.struct = struct
        self.__bits__ = getattr(self.struct, "__bits__", None)

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

    def __size__(self, context: _ContextLike) -> int | EllipsisType:
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
            # Example 1: Packing a fixed-size byte object into the stream
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
    """
    A specialized FieldStruct for handling byte sequences.
    """

    __slots__ = ()

    def __type__(self) -> type:
        """
        Return the type associated with this Bytes field.

        :return: The type (bytes).
        """
        return bytes

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single bytes object from the stream.

        :param context: The current context.
        :return: The unpacked bytes object.
        """
        # as we read bytes from the stream, this will return a bytes object
        return super().unpack_single(context).obj


class String(Bytes):
    """
    A specialized field for handling string data.
    """

    __slots__ = ()

    def __type__(self) -> type:
        """
        Return the type associated with this String field.

        :return: The type (str).
        """
        return str

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single string from the stream.

        :param context: The current context.
        :return: The unpacked string.
        """
        return super().unpack_single(context).decode(self.encoding)


class CString(Bytes):
    """
    A specialized field for handling string data that ends with ``\\0x00``.
    """

    __slots__ = ("pad", "raw_pad")

    def __init__(
        self,
        length: Union[int, _ContextLambda, None] = None,
        encoding: Optional[str] = None,
        pad: Union[str, int, None] = None,
    ) -> None:
        """
        Initialize the String field with a fixed length or a length determined by a context lambda.

        :param length: The fixed length or a context lambda to determine the length dynamically.
        :param encoding: The encoding to use for string encoding/decoding (default is UTF-8).
        """
        super().__init__(length or ...)
        self.encoding = encoding or "utf-8"
        self.pad = pad or 0
        if isinstance(self.pad, str):
            self.pad = ord(self.pad)
        self.raw_pad = self.pad.to_bytes(1, byteorder="big")

    def __type__(self) -> type:
        """
        Return the type associated with this String field.

        :return: The type (str).
        """
        return str

    def pack_single(self, obj: str, context: _ContextLike) -> None:
        """
        Pack a single string into the stream.

        :param obj: The string to pack.
        :param context: The current context.
        """
        encoded = obj.encode(self.encoding)
        if self.length is not Ellipsis:
            length = self.__size__(context)
            obj_length = len(obj)
            payload = encoded + self.raw_pad * (length - obj_length)
        else:
            payload = encoded + self.raw_pad
        super().pack_single(payload, context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single string from the stream.

        :param context: The current context.
        :return: The unpacked string.
        """
        if self.length is Ellipsis:
            # Parse actual C-String
            stream: _StreamType = context[CTX_STREAM]
            data = bytearray()
            while True:
                value = stream.read(1)
                if not value or value == self.raw_pad:
                    break
                data += value
            value = bytes(data)
        else:
            length = self.length(context) if callable(self.length) else self.length
            value: bytes = context[CTX_STREAM].read(length)

        return value.rstrip(self.raw_pad).decode(self.encoding)

    def __class_getitem__(cls, dim) -> Field:
        return CString(...)[dim]


class ConstString(Const):
    """
    A specialized constant field for handling string values.

    :param value: The constant string value.
    :param encoding: The encoding to use for string encoding (default is UTF-8).
    """

    __slots__ = ()

    def __init__(self, value: str, encoding: Optional[str] = None) -> None:
        struct = String(len(value), encoding)
        super().__init__(value.encode(struct.encoding), struct)
        self.__bits__ = len(value) * 8


@registry.TypeConverter(str)
def _str_type_converter(annotation: str, kwargs: dict) -> ConstString:
    return ConstString(annotation)


registry.annotation_registry.append(_str_type_converter)


class ConstBytes(Const):
    """
    A specialized constant field for handling bytes values.

    :param value: The constant bytes value.
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
    __slots__ = ("value",)

    def __init__(self, value: Union[_ConstType, _ContextLambda]) -> None:
        self.value = value
        self.__bits__ = 0

    def __type__(self) -> type:
        return Any if callable(self.value) else type(self.value)

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        pass

    def __size__(self, context: _ContextLike) -> int:
        return 0

    def __unpack__(self, context: _ContextLike) -> Any:
        return self.value(context) if callable(self.value) else self.value

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        # No need for an implementation
        pass

    def unpack_single(self, context: _ContextLike) -> None:
        # No need for an implementation
        pass


@singleton
class Pass(FieldStruct):
    __slots__ = ()

    def __bits__(self) -> int:
        return 0

    def __type__(self) -> type:
        return type(None)

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
    __slots__ = ("encoding", "prefix")

    def __init__(
        self, prefix: Optional[_StructLike] = None, encoding: Optional[str] = None
    ):
        self.encoding = encoding
        self.prefix = prefix or uint32

    def __type__(self) -> type:
        return bytes if not self.encoding else str

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the Prefixed field.

        :param context: The current context.
        :return: The size of the Bytes field.
        """
        raise DynamicSizeError("Prefixed does not store a size", context)

    def pack_single(self, obj: bytes, context: _ContextLike) -> None:
        """
        Pack a single bytes object into the stream.

        :param obj: The bytes object to pack.
        :param context: The current context.
        """
        self.prefix.__pack__(len(obj), context)

        if self.encoding:
            obj = obj.encode(self.encoding)
        context[CTX_STREAM].write(obj)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single bytes object from the stream.

        :param context: The current context.
        :return: The unpacked bytes object.
        """
        size = self.prefix.__unpack__(context)
        data = context[CTX_STREAM].read(size)
        if self.encoding:
            data = data.decode(self.encoding)
        return data


class Int(FieldStruct):
    __slots__ = ("signed", "size")

    def __init__(self, bits: int, signed: bool = True) -> None:
        self.signed = signed
        self.__bits__ = bits
        if not isinstance(bits, int):
            raise ValueError(f"Invalid int size: {bits!r} - expected int")
        self.size = self.__bits__ // 8

    def __type__(self) -> type:
        return int

    def __size__(self, context: _ContextLike) -> int:
        return self.size

    def pack_single(self, obj: int, context: _ContextLike) -> None:
        order = context[CTX_FIELD].order
        byteorder = "little" if order is LittleEndian else "big"
        context[CTX_STREAM].write(
            obj.to_bytes(self.size, byteorder, signed=self.signed)
        )

    def unpack_single(self, context: _ContextLike) -> memoryview:
        order = context[CTX_FIELD].order
        byteorder = "little" if order is LittleEndian else "big"
        return int.from_bytes(
            context[CTX_STREAM].read(self.size), byteorder, signed=self.signed
        )


class UInt(Int):
    __slots__ = ()

    def __init__(self, bits: int) -> None:
        super().__init__(bits, signed=False)


int24 = Int(24)
uint24 = UInt(24)


class Lazy(FieldStruct):
    """
    A lazy field struct that defers the creation of the underlying struct until needed.

    :param struct: A callable that returns the underlying struct.
    """

    def __init__(self, struct: Callable[[], _StructLike]) -> None:
        self.struct_fn = struct

    @cached_property
    def struct(self) -> _StructLike:
        """
        Get the underlying struct.

        :return: The underlying struct.
        :rtype: _StructLike
        """
        return self.struct_fn()

    def __bits__(self) -> str:
        """
        Get the bit representation of the Lazy struct.

        :return: The bit representation.
        :rtype: str
        """
        return self.struct.__bits__()

    def __type__(self) -> type:
        """
        Get the type associated with the Lazy struct.

        :return: The type associated with the Lazy struct.
        :rtype: type
        """
        return self.struct.__type__()

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the Lazy struct.

        :param context: The context for size calculation.
        :return: The size of the Lazy struct.
        :rtype: int
        """
        return self.struct.__size__(context)

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack a single value using the Lazy struct.

        :param Any obj: The value to pack.
        :param context: The context for packing.
        """
        self.struct.__pack__(obj, context)

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single value using the Lazy struct.

        :param context: The context for unpacking.
        :return: The unpacked value.
        """
        return self.struct.__unpack__(context)


@singleton
class uuid(Transformer):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(Bytes(16))

    def __type__(self) -> type:
        return UUID

    def decode(self, parsed: bytes, context) -> UUID:
        return UUID(bytes=parsed)

    def encode(self, obj: UUID, context) -> bytes:
        return obj.bytes


class Pickled(Transformer):
    __slots__ = ()

    def __init__(self, length: Union[int, _ContextLambda]) -> None:
        super().__init__(Bytes(length))

    def __type__(self) -> type:
        return Any

    def decode(self, parsed: bytes, context) -> UUID:
        return pickle.loads(parsed)

    def encode(self, obj: Any, context) -> bytes:
        return pickle.dumps(obj)
