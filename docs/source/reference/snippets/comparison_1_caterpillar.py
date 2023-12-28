from caterpillar.shortcuts import struct, LittleEndian, bitfield, unpack, pack
from caterpillar.fields import uint8, UInt, CString, Prefixed, uint32


@bitfield(order=LittleEndian)
class Flags:
    bool1: 1
    num4: 3
    # padding is generated automatically


@struct(order=LittleEndian)
class Item:
    num1: uint8
    num2: UInt(24)
    flags: Flags
    fixedarray1: uint8[3]
    name1: CString(encoding="utf-8")
    name2: Prefixed(uint8, encoding="utf-8")


Format = LittleEndian + Item[uint32::]
