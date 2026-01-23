from caterpillar.py import struct, uint16, pack
from caterpillar.shortcuts import f, this, Dynamic, BigEndian
from caterpillar.types import uint32_t, uint8_t

MY_BIG_ENDIAN_ID = 0
MY_LITTLE_ENDIAN_ID = 1


@struct(order=BigEndian, kw_only=True)
class Format:
    spec: uint8_t = MY_BIG_ENDIAN_ID

    a: f[int, Dynamic(this.spec) + uint16]
    # also possible
    # a: f[int, uint16, Dynamic(this.spec)]
    b: uint32_t


obj_be = Format(spec=MY_BIG_ENDIAN_ID, a=0x1234, b=0x56789ABC)
data_be = pack(obj_be)
obj_le = Format(spec=MY_LITTLE_ENDIAN_ID, a=0x1234, b=0x56789ABC)
data_le = pack(obj_le)

assert data_le[1:] != data_be[1:]
print(obj_be, obj_le)
print("BE:", data_be)
print("LE:", data_le)
