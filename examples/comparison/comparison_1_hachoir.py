from hachoir.field import *
from hachoir.stream import StringInputStream
from hachoir.core.bits import LITTLE_ENDIAN


class Entry(FieldSet):
    endian = LITTLE_ENDIAN

    def createFields(self):
        yield UInt8(self, "num1")
        yield UInt24(self, "num2")
        yield Bit(self, "bool1")
        yield Bits(self, "num4", 3)
        yield PaddingBits(self, "_", 4)
        for _ in range(3):
            yield UInt8(self, "fixedarray[]")
        yield CString(self, "name1")
        yield PascalString8(self, "name2")


class Format(Parser):
    endian = LITTLE_ENDIAN

    def createFields(self):
        yield UInt32(self, "count")
        for _ in range(self["count"].value):
            yield Entry(self, "entry[]")


if __name__ == "__main__":
    import sys
    import timeit

    try:
        from rich import print
    except ImportError:
        pass

    with open(sys.argv[1], "rb") as fp:
        data = fp.read()

    time = (
        timeit.timeit(lambda: list(Format(StringInputStream(data))), number=1000) / 1000
    )
    print("[bold]Parsing measurements:[/]")
    print(f"[bold]default[/]  {time:.10f} sec/call")
