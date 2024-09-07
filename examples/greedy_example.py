# type: ignore
from caterpillar.py import struct, BigEndian, this, unpack, uint8

try:
    from rich import print
except ImportError:
    pass


@struct(order=BigEndian)
class Format:
    magic: b"BMP"
    width: uint8
    height: uint8
    pixels: uint8[this.width * this.height]


@struct(order=BigEndian)
class Format2:
    magic: b"BMP"
    width: uint8
    height: uint8
    pixels: uint8[...]


print(unpack(Format[...], b"BMP\x02\x02\x00\x01\x02\x03BMP\x00\x00"))
# Prints:
# [Format(magic=b'BMP', width=2, height=2, pixels=[0, 1, 2, 3]), Format(magic=b'BMP', width=0, height=0, pixels=[])]
# and
print(unpack(Format2[...], b"BMP\x02\x02\x00\x01\x02\x03BMP\x00\x00"))
# prints:
# [Format2(magic=b'BMP', width=2, height=2, pixels=[0, 1, 2, 3, 66, 77, 80, 0, 0])]
