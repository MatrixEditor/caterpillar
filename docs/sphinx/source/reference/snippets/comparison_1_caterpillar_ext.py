import typing
from caterpillar.py import *
from caterpillar.types import *


@bitfield(order=LittleEndian)
class Flags:
    bool1: int1_t
    num4: int3_t
    # padding is generated automatically


@struct(order=LittleEndian)
class Item(struct_factory.mixin):
    num1: uint8_t
    num2: uint24_t
    flags: Flags
    fixedarray1: f[list[int], uint8[3]]
    name1: cstr_t
    name2: f[bytes, Prefixed(uint8, encoding="utf-8")]


Format = Item[LittleEndian + uint32 : :]
