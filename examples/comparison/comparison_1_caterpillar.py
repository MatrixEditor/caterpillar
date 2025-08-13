from caterpillar.shortcuts import struct, LittleEndian, bitfield, unpack, pack
from caterpillar.fields import uint8, uint24, CString, Prefixed, uint32


# The __slots__ options does not affect the packing or
# unpacking process.
# opt.set_struct_flags(opt.S_SLOTS, opt.S_REPLACE_TYPES)

# The following lines will reduce the time around 10% for
# packing and unpacking. (C-Extension required)
# from caterpillar.context import O_CONTEXT_FACTORY
# from caterpillar.c import c_Context
# O_CONTEXT_FACTORY.value = c_Context

@bitfield(order=LittleEndian)
class Flags:
    bool1: 1
    num4: 3
    # padding is generated automatically


@struct(order=LittleEndian)
class Item:
    num1: uint8
    num2: uint24
    flags: Flags
    fixedarray1: uint8[3]
    name1: CString()
    # Replacing the encoding with String(...) makes a huge difference
    # as we don't call .decode() directly
    #
    # Time goes down from 0.0119 to 0.0099 for unpacking
    # and from 0.0094 to 0.0082 for packing
    name2: Prefixed(uint8, encoding="utf-8")


# makes no real difference
# @struct(order=LittleEndian)
# class Format:
#     items: Item[uint32::]

Format = LittleEndian + Item[uint32::]

if __name__ == "__main__":
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
