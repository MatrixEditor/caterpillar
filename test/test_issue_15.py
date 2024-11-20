from caterpillar.py import *


@struct
class StructThreeInts:
    v1: uint8
    v2: uint8
    v3: uint8


@struct
class Format:
    flag: uint8
    with this.flag == 1:
        optional_ints: StructThreeInts


s = b"\x01\x01\x02\x03\xFF"
o = unpack(Format[2], s)
print(o)
