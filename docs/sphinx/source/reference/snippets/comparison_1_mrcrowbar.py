from mrcrowbar.fields import Bits8, UInt24_LE, UInt32_LE, BlockField, UInt8
from mrcrowbar.models import Block, CString, CStringN
from mrcrowbar.refs import Ref


class Entry(Block):
    num1 = UInt8()
    num2 = UInt24_LE()
    bool1 = Bits8(0x0004, bits=0b10000000, endian="little")
    num4 = Bits8(0x0004, bits=0b01110000, endian="little")
    fixedarray1 = UInt8(0x0005, count=3)
    name1 = CString(0x0008)
    name2 = CString(length_field=UInt8)


class Format(Block):
    count = UInt32_LE(0x0000)
    entries = BlockField(Entry, 0x0004, count=Ref("count"))
