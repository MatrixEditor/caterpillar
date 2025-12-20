from caterpillar.byteorder import Dynamic, BigEndian
from caterpillar.context import this
from caterpillar.py import struct, uint16, uint32, uint8, pack, unpack

MY_BIG_ENDIAN_ID = 0
MY_LITTLE_ENDIAN_ID = 1

@struct(order=BigEndian)
class Format:
    spec: uint8 = MY_BIG_ENDIAN_ID

    a: Dynamic(this.spec) + uint16
    b: uint32

obj_be = Format(spec=MY_BIG_ENDIAN_ID, a=0x1234, b=0x56789abc)
data_be = pack(obj_be)
obj_le = Format(spec=MY_LITTLE_ENDIAN_ID, a=0x1234, b=0x56789abc)
data_le = pack(obj_le)

assert data_le[1:] != data_be[1:]
print(obj_be, obj_le)
print("BE:", data_be)
print("LE:", data_le)