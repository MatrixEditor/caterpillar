import typing
from caterpillar.py import Field, f
from caterpillar.shortcuts import struct, LittleEndian, bitfield, unpack, pack
from caterpillar.fields import uint8, Prefixed, uint32
from caterpillar.types import cstr_t, int1_t, int3_t, uint24_t, uint8_t


# The __slots__ options does not affect the packing or
# unpacking process.
# from caterpillar import options as opt
# opt.set_struct_flags(opt.S_SLOTS, opt.S_REPLACE_TYPES)

# The following lines will reduce the time around 10% for
# packing and unpacking. (C-Extension required)
# from caterpillar.context import O_CONTEXT_FACTORY
# from caterpillar.c import c_Context
# O_CONTEXT_FACTORY.value = c_Context


@bitfield(order=LittleEndian)
class Flags:
    bool1: int1_t
    num4: int3_t
    # padding is generated automatically


@struct(order=LittleEndian)
class Item:
    num1: uint8_t
    num2: uint24_t
    flags: Flags
    fixedarray1: f[list[int], uint8[3]]
    name1: cstr_t
    # Replacing the encoding with String(...) makes a huge difference
    # as we don't call .decode() directly
    #
    # Time goes down from 0.0119 to 0.0099 for unpacking
    # and from 0.0094 to 0.0082 for packing
    name2: f[bytes, Prefixed(uint8, encoding="utf-8")]

    if typing.TYPE_CHECKING:

        def __class_getitem__(cls, length) -> Field: ...


# makes no real difference
# @struct(order=LittleEndian)
# class Format:
#     items: Item[uint32::]

Format = Item[LittleEndian + uint32 : :]

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
