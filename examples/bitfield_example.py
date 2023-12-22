from caterpillar.shortcuts import *
from caterpillar.fields import *

try:
    from rich import print
except ImportError:
    pass


@bitfield
class Format:
    b1  : 1             # inferred uint8 type with a width of one bit
    _   : 0             # start new uint8 with 7 unused bits
    b2  : 2 - char      # wraps parsed int to char (string)
    b3  : 3 - int8 = 1  # default value is applied -> REVISIT: necessary?
    _1  : 3             # unnamed padding to the rest of the byte

print(Format.__struct__)
obj = unpack(Format, b"\x01\x01")
print(obj)
# prints: Format(b1=True, b2='1', b3=0, _1=0)
# because:       0000000100000001
# breakdown is:  \_/\_/\/\_____/|
#                 u b3 b2   a   b1
# where 'u' marks unused bits (the field name starts with an underscore and
# contains only numbers). The field named '_' is a special definition for
# alignment, missing bits will be added automatically (marked with 'a' in
# breakdown).

print(pack(obj))
# prints: b'\x01\x01'
