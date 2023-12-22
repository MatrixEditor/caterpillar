from caterpillar.fields.varint import VarInt, VARINT_LSB
from caterpillar.shortcuts import pack, unpack, BigEndian as be, LittleEndian as le

try:
    from rich import print
except ImportError:
    pass

fields = {
    "be + VarInt": be + VarInt,
    "be + VarInt | VARINT_LSB": be + VarInt | VARINT_LSB,
    "le + VarInt": le + VarInt,
    "le + VarInt | VARINT_LSB": le + VarInt | VARINT_LSB,
}

value = 1024
print(f"Value: {value}")

for name, field in fields.items():
    print(f"Field {name}:")
    data = pack(value, field)
    print(f" << {data}")
    print(f" >> {unpack(field, data)}")

# Output should be:
# Value: 1024
# Field be + VarInt:
#  << b'\x88\x00'
#  >> 1024
# Field be + VarInt | VARINT_LSB:
#  << b'\x08\x80'
#  >> 1024
# Field le + VarInt:
#  << b'\x80\x08'
#  >> 1024
# Field le + VarInt | VARINT_LSB:
#  << b'\x00\x88'
#  >> 1024
