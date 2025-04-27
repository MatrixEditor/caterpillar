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
from __future__ import annotations

from typing import Any

from caterpillar.abc import _StreamType, _ContextLike
from caterpillar.exception import InvalidValueError, DynamicSizeError, StreamError
from caterpillar.byteorder import LittleEndian
from caterpillar.context import CTX_FIELD, CTX_STREAM
from caterpillar.options import Flag

from ._mixin import FieldStruct


VARINT_LSB = Flag("varint.lsb")


class VarInt(FieldStruct):
    """Variable-length integer struct.

    This class implements variable-length unsigned integer for big-endian and
    little-endian encoding. The default behaviour uses big-endian encoding. It
    has an additional flag that can be configured globally or once per field.

    ``VARINT_LSB`` specifies that the last significant byte will use a ``1`` to
    identify the end of the varint. Otherwise, zero will be used (which is the
    default setting). The following configurations are therefore possible:

    >>> field = be + vint; print(pack(1024, field))
    b'\\x88\\x00'
    >>> field = be + vint | VARINT_LSB; print(pack(1024, field))
    b'\\x08\\x80'
    >>> field = le + vint; print(pack(1024, field))
    b'\\x80\\x08'
    >>> field = le + vint | VARINT_LSB; print(pack(1024, field))
    b'\\x00\\x88'
    """

    __slots__ = ()

    def __type__(self) -> type:
        return int

    def __size__(self, context: _ContextLike) -> int:
        raise DynamicSizeError("VarInt has dynamic size!")

    def bit_config(self, context: _ContextLike) -> tuple:
        high_bit = 1 << 7
        low_bit = 0
        if context[CTX_FIELD].has_flag(VARINT_LSB):
            high_bit = 0
            low_bit = 1 << 7
        return high_bit, low_bit

    def pack_single(self, obj: int, context: _ContextLike) -> None:
        """
        Pack a single value into the stream.

        :param obj: The value to pack.
        :param context: The current context.
        """
        if obj is None:
            raise InvalidValueError("NoneType can't be interpreted as a VarInt!")

        if obj < 0:
            raise InvalidValueError("Invalid negative value for VarInt encoding!")

        stream: _StreamType = context[CTX_STREAM]
        order = context[CTX_FIELD].order
        is_little = order == LittleEndian

        hb, lb = self.bit_config(context)
        # This implementation is using LittleEndian. Later we can use reverse to
        # apply little endian encoding.
        data = []
        while obj > 0b01111111:
            data.append(obj & 0x7F)
            obj >>= 7
        data.append(obj)

        if not is_little:
            data.reverse()

        for i in range(0, len(data) - 1):
            data[i] |= hb

        data[-1] |= lb
        # Just write all bytes to the stream
        stream.write(bytes(data))

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Unpack a single value from the stream.

        :param stream: The input stream.
        :param context: The current context.
        :return: The unpacked value.
        """
        stream: _StreamType = context[CTX_STREAM]
        data = []
        _, lb = self.bit_config(context)
        shift = 0
        is_little = context[CTX_FIELD].order == LittleEndian

        while True:
            # Note tha unpack operation here to retrieve one byte only
            try:
                (value,) = stream.read(1)
            except ValueError as exc:
                raise StreamError("Can't read stream!", context) from exc
            data.append(value & 0x7F)
            if value & 0x80 == lb:
                # The "low_byte" here is taken from the field's configuration
                break

        # The following examples shows what to do with the byteorder
        # configuration: num=0xA0B0C0D0
        #                            0     1     2     3
        # b'\xd0\xc0\xb0\xa0' LE : [0xD0, 0xC0, 0xB0, 0xA0]
        # b'\xa0\xb0\xc0\xd0' BE : [0xA0, 0xB0, 0xC0, 0xD0] << reverse that
        if not is_little:
            data.reverse()
        value = 0
        for number in data:
            value |= number << shift
            shift += 7
        return value


vint = VarInt()
