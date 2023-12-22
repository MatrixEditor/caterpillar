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
from __future__ import annotations

from struct import calcsize, pack, unpack
from typing import Sequence, Any, Optional, Union, List
from enum import Enum as _EnumType

from caterpillar.abc import (
    _StructLike,
    _ContextLike,
    _StreamType,
    _ContextLambda,
    _EnumLike,
)
from caterpillar.exception import ValidationError, UnsupportedOperation, StructException

from ._base import Field, FieldStruct


class FormatField(FieldStruct):
    """
    A field class representing a binary format. It inherits from FieldStruct.
    """

    def __init__(self, ch: str, type_: type) -> None:
        """
        Initialize the FormatField.

        :param ch: The format specifier text.
        :param type_: The Python type associated with the format specifier.
        """
        self.text = ch
        self.type_ = type_
        self.__bits__ = calcsize(self.text)

    def __repr__(self) -> str:
        """
        String representation of the FormatField.

        :return: A string representation.
        """
        type_repr = self.type_.__name__ if not self.is_padding() else "padding"
        return f"<{self.__class__.__name__}({type_repr}) {self.text!r}>"

    def __type__(self) -> type:
        """
        Get the Python type associated with the format specifier.

        :return: The Python type.
        """
        return self.type_

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the field.

        :param context: The current context.
        :return: The size of the field.
        """
        return calcsize(self.get_format(context))

    def pack_single(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        """
        Pack a single value into the stream.

        :param obj: The value to pack.
        :param stream: The output stream.
        :param context: The current context.
        """
        if obj is None:
            values = []
        else:
            values = obj if isinstance(obj, list) else [obj]

        if len(values) == 0 and not self.is_padding():
            return
        data = pack(self.get_format(context), *values)
        stream.write(data)

    def pack_seq(
        self, seq: Sequence, stream: _StreamType, context: _ContextLike
    ) -> None:
        """
        Pack a sequence of values into the stream.

        :param seq: The sequence of values.
        :param stream: The output stream.
        :param context: The current context.
        """
        self.pack_single(seq, stream, context)

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> Any:
        """
        Unpack a single value from the stream.

        :param stream: The input stream.
        :param context: The current context.
        :return: The unpacked value.
        """
        length = context._field.length(context)
        if length == 0 and context._field.is_seq():
            # REVISIT: maybe add factory here
            return []

        fmt = self.get_format(context, length or 1)
        try:
            value = unpack(fmt, stream.read(calcsize(fmt)))
        except ValueError as exc:
            raise StructException(f"unpack() - Error at {context._path}") from exc

        if not context._field.is_seq():
            if len(value) == 0:
                value = None
            else:
                value, *_ = value

        return value

    def unpack_seq(self, stream: _StreamType, context: _ContextLike) -> List[Any]:
        """
        Unpack a sequence of values from the stream.

        :param stream: The input stream.
        :param context: The current context.
        :return: A list of unpacked values.
        """
        return list(self.unpack_single(stream, context))

    def get_format(self, context: _ContextLike, length: int = None) -> str:
        """
        Get the format string for the field.

        :param context: The current context.
        :return: The format string.
        """
        field: Field = context._field

        order = field.order
        if length is None:
            dim = field.length(context) or 1
        else:
            dim = length
        return f"{order.ch}{dim}{self.text}"

    def is_padding(self) -> bool:
        """
        Check if the field represents padding.

        :return: True if the field is padding, False otherwise.
        """
        return self.text == "x"


# Instances of FormatField with specific format specifiers
padding = FormatField("x", None)
char = FormatField("c", str)
boolean = FormatField("?", bool)

int8 = FormatField("b", int)
uint8 = FormatField("B", int)
int16 = FormatField("h", int)
uint16 = FormatField("H", int)
int32 = FormatField("i", int)
uint32 = FormatField("I", int)
int64 = FormatField("l", int)
uint64 = FormatField("L", int)
int128 = FormatField("q", int)
uint128 = FormatField("Q", int)

ssize_t = FormatField("n", int)
size_t = FormatField("N", int)

float32 = FormatField("f", float)
float64 = FormatField("d", float)
double = float64

void_ptr = FormatField("P", int)
unsigned = uint32
signed = int32

_ConstType = Union[str, bytes, Any]


class Transformer(FieldStruct):
    """
    A class that acts as a transformer for encoding and decoding data using a wrapped _StructLike object.
    """

    def __init__(self, struct: _StructLike) -> None:
        """
        Initialize the Transformer with a wrapped _StructLike object.

        :param struct: The _StructLike object to be wrapped.
        """
        self.struct = struct
        self.__bits__ = getattr(self.struct, "__bits__", None)

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

    def pack_single(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        """
        Pack a single value into the stream using encoding.

        :param obj: The original data to be encoded and packed.
        :param stream: The output stream.
        :param context: The current context.
        """
        value = self.encode(obj, context)
        self.struct.__pack__(value, stream, context)

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> Any:
        """
        Unpack a single value from the stream and decode it.

        :param stream: The input stream.
        :param context: The current context.
        :return: The decoded data.
        """
        value = self.struct.__unpack__(stream, context)
        return self.decode(value, context)


class Const(Transformer):
    """
    A specialized Transformer that enforces a constant value during encoding and decoding.
    """

    def __init__(self, value: _ConstType, struct: _StructLike) -> None:
        """
        Initialize the Const transformer with a constant value and a wrapped _StructLike object.

        :param value: The constant value to be enforced during encoding and decoding.
        :param struct: The _StructLike object to be wrapped.
        """
        super().__init__(struct)
        self.value = value

    def encode(self, obj: Any, context: _ContextLike) -> Any:
        """
        Encode data using the constant value.

        :param obj: The original data to be encoded (ignored).
        :param context: The current context.
        :return: The constant value.
        """
        return self.value

    def decode(self, parsed: Any, context: _ContextLike) -> Any:
        """
        Decode data and ensure it matches the constant value.

        :param parsed: The parsed data to be decoded.
        :param context: The current context.
        :return: The constant value.
        :raises ValidationError: If the parsed value does not match the constant value.
        """
        if parsed != self.value:
            raise ValidationError(
                f"Expected {str(self.value)}, got {str(parsed)} in {context._path}"
            )
        return self.value


class Enum(Transformer):
    """
    A specialized Transformer for encoding and decoding enumeration values.
    """

    def __init__(
        self, model: _EnumLike, struct: _StructLike, default: Optional[_EnumLike] = None
    ) -> None:
        """
        Initialize the Enum transformer with an enumeration model and a wrapped _StructLike object.

        :param model: The enumeration model (an object with _member_map_ and _value2member_map_ attributes).
        :param struct: The _StructLike object to be wrapped.
        """
        super().__init__(struct)
        self.model = model
        self.default = default

    def encode(self, obj: Any, context: _ContextLike) -> Any:
        """
        Encode an enumeration value.

        :param obj: The original enumeration value.
        :param context: The current context.
        :return: The encoded value (integer).
        :raises ValidationError: If the input is not an enumeration type.
        """
        if isinstance(obj, _EnumType):
            return obj.value

        raise ValidationError(f"Expected enum type, got {type(obj)}")

    def decode(self, parsed: Any, context: _ContextLike) -> Any:
        """
        Decode an integer value to its corresponding enumeration value.

        :param parsed: The parsed integer value.
        :param context: The current context.
        :return: The corresponding enumeration value.
        """
        by_name = self.model._member_map_.get(parsed)
        by_value = self.model._value2member_map_.get(parsed)
        return by_name or by_value or self.default


class Bytes(FieldStruct):
    """
    A specialized FieldStruct for handling byte sequences.
    """

    def __init__(self, length: Union[int, _ContextLambda]) -> None:
        """
        Initialize the Bytes field with a fixed length or a length determined by a context lambda.

        :param length: The fixed length or a context lambda to determine the length dynamically.
        """
        self.length = length

    def __type__(self) -> type:
        """
        Return the type associated with this Bytes field.

        :return: The type (bytes).
        """
        return bytes

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the Bytes field.

        :param context: The current context.
        :return: The size of the Bytes field.
        """
        return self.length(context) if callable(self.length) else self.length

    def pack_single(
        self, obj: bytes, stream: _StreamType, context: _ContextLike
    ) -> None:
        """
        Pack a single bytes object into the stream.

        :param obj: The bytes object to pack.
        :param stream: The output stream.
        :param context: The current context.
        """
        stream.write(obj)

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> Any:
        """
        Unpack a single bytes object from the stream.

        :param stream: The input stream.
        :param context: The current context.
        :return: The unpacked bytes object.
        """
        size = self.__size__(context)
        return stream.read(size)

    def get_format(self, context: _ContextLike) -> str:
        """
        Get the format string associated with this Bytes field.

        :param context: The current context.
        :return: The format string.
        """
        field: Field = context._field
        order = field.order
        dim = self.__size__(context)
        return f"{order.ch}{dim}s"

    def __class_getitem__(self, dim: int) -> None:
        """
        Class method to raise an UnsupportedOperation when attempting to use multiple sequences.

        :param dim: The dimension (length) of the sequence.
        :raises UnsupportedOperation: Multiple sequences not allowed!
        """
        raise UnsupportedOperation("Multiple sequences not allowed!")


class String(Bytes):
    """
    A specialized field for handling string data.
    """

    def __init__(
        self, length: Union[int, _ContextLambda], encoding: Optional[str] = None
    ) -> None:
        """
        Initialize the String field with a fixed length or a length determined by a context lambda.

        :param length: The fixed length or a context lambda to determine the length dynamically.
        :param encoding: The encoding to use for string encoding/decoding (default is UTF-8).
        """
        super().__init__(length)
        self.encoding = encoding or "utf-8"

    def __type__(self) -> type:
        """
        Return the type associated with this String field.

        :return: The type (str).
        """
        return str

    def pack_single(self, obj: str, stream: _StreamType, context: _ContextLike) -> None:
        """
        Pack a single string into the stream.

        :param obj: The string to pack.
        :param stream: The output stream.
        :param context: The current context.
        """
        super().pack_single(obj.encode(self.encoding), stream, context)

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> Any:
        """
        Unpack a single string from the stream.

        :param stream: The input stream.
        :param context: The current context.
        :return: The unpacked string.
        """
        return super().unpack_single(stream, context).decode(self.encoding)


class CString(Bytes):
    """
    A specialized field for handling string data that ends with ``\\0x00``.
    """

    def __init__(
        self, length: Union[int, _ContextLambda], encoding: Optional[str] = None
    ) -> None:
        """
        Initialize the String field with a fixed length or a length determined by a context lambda.

        :param length: The fixed length or a context lambda to determine the length dynamically.
        :param encoding: The encoding to use for string encoding/decoding (default is UTF-8).
        """
        super().__init__(length)
        self.encoding = encoding or "utf-8"

    def __type__(self) -> type:
        """
        Return the type associated with this String field.

        :return: The type (str).
        """
        return str

    def pack_single(self, obj: str, stream: _StreamType, context: _ContextLike) -> None:
        """
        Pack a single string into the stream.

        :param obj: The string to pack.
        :param stream: The output stream.
        :param context: The current context.
        """
        length = self.__size__(context)
        obj_length = len(obj)
        payload = obj.encode(self.encoding) + b"\x00" * (length - obj_length)
        super().pack_single(payload, stream, context)

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> Any:
        """
        Unpack a single string from the stream.

        :param stream: The input stream.
        :param context: The current context.
        :return: The unpacked string.
        """
        value: str = super().unpack_single(stream, context).decode(self.encoding)
        return value.rstrip("\x00")


class ConstString(Const):
    """
    A specialized constant field for handling string values.
    """

    def __init__(self, value: str, encoding: Optional[str] = None) -> None:
        """
        Initialize the ConstString field with a constant string value.

        :param value: The constant string value.
        :param encoding: The encoding to use for string encoding (default is UTF-8).
        """
        struct = String(len(value), encoding)
        super().__init__(value.encode(struct.encoding), struct)


class ConstBytes(Const):
    """
    A specialized constant field for handling bytes values.
    """

    def __init__(self, value: str) -> None:
        """
        Initialize the ConstBytes field with a constant bytes value.

        :param value: The constant bytes value.
        """
        super().__init__(value, Bytes(len(value)))


class Computed(FieldStruct):
    def __init__(self, value: Union[_ConstType, _ContextLambda]) -> None:
        self.value = value

    def __type__(self) -> type:
        return Any if callable(self.value) else type(self.value)

    def __pack__(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        pass

    def __size__(self, context: _ContextLike) -> int:
        return 0

    def __unpack__(self, stream: _StreamType, context: _ContextLike) -> Any:
        return self.value(context) if callable(self.value) else self.value

    def pack_single(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        # No need for an implementation
        pass

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> None:
        # No need for an implementation
        pass


class Pass(FieldStruct):
    def __type__(self) -> type:
        return type(None)

    def __pack__(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        pass

    def __size__(self, context: _ContextLike) -> int:
        return 0

    def __unpack__(self, stream: _StreamType, context: _ContextLike) -> Any:
        return None

    def pack_single(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        # No need for an implementation
        pass

    def unpack_single(self, stream: _StreamType, context: _ContextLike) -> None:
        # No need for an implementation
        pass
