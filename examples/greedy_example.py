import typing

from caterpillar.shortcuts import f
from caterpillar.py import struct, BigEndian, this, unpack, uint8
from caterpillar.abc import _LengthT  # pyright: ignore[reportPrivateUsage]
from caterpillar.types import uint8_t


BMP_MAGIC = b"BMP"
# reusable types can be defined using the f[...] shortcut
magic_t = f[bytes, BMP_MAGIC]


@struct(order=BigEndian, kw_only=True)
class Format:
    magic: magic_t = BMP_MAGIC
    width: uint8_t
    height: uint8_t
    pixels: f[list[int], uint8[this.width * this.height]]

    # Workaround for typing issues when using Class[...]
    if typing.TYPE_CHECKING:

        def __class_getitem__(cls, length: _LengthT): ...


@struct(order=BigEndian, kw_only=True)
class Format2:
    magic: magic_t = BMP_MAGIC
    width: uint8_t
    height: uint8_t
    pixels: f[list[int], uint8[...]]

    if typing.TYPE_CHECKING:

        def __class_getitem__(cls, length: _LengthT): ...


print(unpack(Format[...], b"BMP\x02\x02\x00\x01\x02\x03BMP\x00\x00"))
# Prints:
# [Format(magic=b'BMP', width=2, height=2, pixels=[0, 1, 2, 3]), Format(magic=b'BMP', width=0, height=0, pixels=[])]
# and
x = Format2[...]
print(unpack(Format2[...], b"BMP\x02\x02\x00\x01\x02\x03BMP\x00\x00"))
# prints:
# [Format2(magic=b'BMP', width=2, height=2, pixels=[0, 1, 2, 3, 66, 77, 80, 0, 0])]
