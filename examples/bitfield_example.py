# type: ignore
import typing
from caterpillar.py import (
    Bitfield,
    bitfield,
    CharFactory,
    getstruct,
    int8,
    unpack,
    pack,
)
from caterpillar.shortcuts import f
from caterpillar.types import int1_t, int3_t


@bitfield
class Format:
    b1: int1_t                    # inferred uint8 type with a width of one bit
    if not typing.TYPE_CHECKING:
        _: 0                      # start new uint8 with 7 unused bits
    b2: f[str, (2, CharFactory)]  # wraps parsed int to char (string)
    b3: f[int, 3 - int8] = 1      # default value is applied -> REVISIT: necessary?
    _1: int3_t                    # unnamed padding to the rest of the byte


s = getstruct(Format)
assert isinstance(s, Bitfield)
print(s.groups)
obj = unpack(Format, b"\x80\x80")
print(obj)
# prints: Format(b1=1, b2='\x02', b3=0, _1=0)
# real_pos:      0123456701234567
# bit_pos:       7654321076543210
#                ---------------- # right to left
# because:       1000000010000000
# breakdown is:  |\_____/\/\_/\_/
#                b1  a   b2 b3 u
# where 'u' marks unused bits (the field name starts with an underscore and
# contains only numbers). The field named '_' is a special definition for
# alignment, missing bits will be added automatically (marked with 'a' in
# breakdown).

print(pack(obj))
# prints: b'\x80\x80'
