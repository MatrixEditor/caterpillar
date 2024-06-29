from caterpillar.model import struct, sizeof
from caterpillar.fields import uint16, _infix_
from caterpillar.options import S_REPLACE_TYPES

# Here, we define a custom operator named 'M' that will multiply
# the second argument by 2.
M = _infix_(lambda a, b: a[b*2])

# or directly as function
# @_infix_
# def M(a, b):
#     return a[b*2]

@struct(options={S_REPLACE_TYPES})
class Format:
    # __annotations__ should contain typing.List[int] as we've specified the
    # documentation option.
    f1: uint16 /M/ 3

print(Format.__annotations__)

