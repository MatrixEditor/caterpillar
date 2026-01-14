from caterpillar.py import struct, uint16, uint32, uint8, pack
from caterpillar.shortcuts import f, this, Dynamic, BigEndian

MY_BIG_ENDIAN_ID = 0
MY_LITTLE_ENDIAN_ID = 1


@struct(order=BigEndian)
class Format:
    spec: f[int, uint8] = MY_BIG_ENDIAN_ID

    a: f[int, Dynamic(this.spec) + uint16]
    b: f[int, uint32]


obj_be = Format(spec=MY_BIG_ENDIAN_ID, a=0x1234, b=0x56789ABC)
data_be = pack(obj_be)
obj_le = Format(spec=MY_LITTLE_ENDIAN_ID, a=0x1234, b=0x56789ABC)
data_le = pack(obj_le)

assert data_le[1:] != data_be[1:]
print(obj_be, obj_le)
print("BE:", data_be)
print("LE:", data_le)
