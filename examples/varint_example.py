# type: ignore
from caterpillar.py import (
    vint,
    VARINT_LSB,
    pack,
    unpack,
    BigEndian as be,
    LittleEndian as le,
)

try:
    from rich import print
except ImportError:
    pass

fields = {
    "be + vint": be + vint,
    "be + vint | VARINT_LSB": be + vint | VARINT_LSB,
    "le + vint": le + vint,
    "le + vint | VARINT_LSB": le + vint | VARINT_LSB,
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
# Field be + vint:
#  << b'\x88\x00'
#  >> 1024
# Field be + vint | VARINT_LSB:
#  << b'\x08\x80'
#  >> 1024
# Field le + vint:
#  << b'\x80\x08'
#  >> 1024
# Field le + vint | VARINT_LSB:
#  << b'\x00\x88'
#  >> 1024
