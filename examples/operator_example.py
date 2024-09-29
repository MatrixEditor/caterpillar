# type: ignore
from caterpillar.py import struct, uint16, Operator, S_REPLACE_TYPES

# Here, we define a custom operator named 'M' that will multiply
# the second argument by 2.
M = Operator(lambda a, b: a[b*2])

# or directly as function
# @Operator
# def M(a, b):
#     return a[b*2]

@struct(options={S_REPLACE_TYPES})
class Format:
    # __annotations__ should contain typing.List[int] as we've specified the
    # documentation option.
    f1: uint16 /M/ 3

print(Format.__annotations__)

