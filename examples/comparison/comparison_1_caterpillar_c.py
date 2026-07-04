import typing

import caterpillar
from caterpillar.context import O_CONTEXT_FACTORY
from caterpillar.fields import Prefixed, uint8, uint32
from caterpillar.py import Field, f
from caterpillar.shortcuts import bitfield, pack, struct, unpack
from caterpillar.types import cstr_t, int1_t, int3_t, uint24_t, uint8_t

if not caterpillar.native_support():
    raise RuntimeError("The native Caterpillar extension is required for this example")

from caterpillar.c import LITTLE_ENDIAN, Repeated, c_Context


@bitfield(order=LITTLE_ENDIAN)
class Flags:
    bool1: int1_t
    num4: int3_t
    # padding is generated automatically


@struct(order=LITTLE_ENDIAN)
class Item:
    num1: uint8_t
    num2: uint24_t
    flags: Flags
    fixedarray1: f[list[int], uint8[3]]
    name1: cstr_t
    name2: f[str, Prefixed(uint8, encoding="utf-8")]

    if typing.TYPE_CHECKING:

        def __class_getitem__(cls, length) -> Field: ...


Format = Repeated(Item, slice(LITTLE_ENDIAN + uint32, None, None))


if __name__ == "__main__":
    import sys
    import timeit

    try:
        from rich import print
    except ImportError:
        pass

    with open(sys.argv[1], "rb") as fp:
        data = fp.read()

    old_factory = O_CONTEXT_FACTORY.value
    O_CONTEXT_FACTORY.value = c_Context
    try:
        obj = unpack(Format, data)
        time = timeit.timeit(lambda: unpack(Format, data), number=1000) / 1000
        print("[bold]Timeit measurements:[/]")
        print(f"[bold]unpack[/] {time:.10f} sec/call")

        ptime = timeit.timeit(lambda: pack(obj, Format), number=1000) / 1000
        print(f"[bold]pack[/]   {ptime:.10f} sec/call")
    finally:
        O_CONTEXT_FACTORY.value = old_factory
