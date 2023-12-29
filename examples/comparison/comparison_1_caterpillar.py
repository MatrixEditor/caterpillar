from caterpillar.shortcuts import struct, LittleEndian, bitfield, unpack, pack
from caterpillar.fields import uint8, UInt, CString, Prefixed, uint32


@bitfield(order=LittleEndian)
class Flags:
    bool1 : 1
    num4  : 3
    # padding is generated automatically


@struct(order=LittleEndian)
class Item:
    num1: uint8
    num2: UInt(24)
    flags: Flags
    fixedarray1: uint8[3]
    name1: CString(encoding="utf-8")
    name2: Prefixed(uint8, encoding="utf-8")


# makes no real difference
# @struct(order=LittleEndian)
# class Format:
#     items: Item[uint32::]

Format = LittleEndian + Item[uint32::]

if __name__ == '__main__':
    import sys
    import timeit

    try:
        from rich import print
    except ImportError:
        pass

    with open(sys.argv[1], "rb") as fp:
        data = fp.read()

    obj = unpack(Format, data)
    time = timeit.timeit(lambda: unpack(Format, data), number=1000) / 1000
    print("[bold]Timeit measurements:[/]")
    print(f"[bold]unpack[/] {time:.10f} sec/call")

    ptime = timeit.timeit(lambda: pack(obj, Format), number=1000) / 1000
    print(f"[bold]pack[/]   {ptime:.10f} sec/call")
