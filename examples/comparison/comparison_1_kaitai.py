# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, "API_VERSION", (0, 9)) < (0, 9):
    raise Exception(
        "Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s"
        % (kaitaistruct.__version__)
    )


class Comparison1Kaitai(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.count = self._io.read_u4le()
        self.items = []
        for i in range(self.count):
            self.items.append(Comparison1Kaitai.Item(self._io, self, self._root))

    class Item(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num1 = self._io.read_u1()
            self.num2_lo = self._io.read_u2le()
            self.num2_hi = self._io.read_u1()
            self.flags = Comparison1Kaitai.Item.Flags(self._io, self, self._root)
            self.fixedarray1 = []
            for i in range(3):
                self.fixedarray1.append(self._io.read_u1())

            self.name1 = (self._io.read_bytes_term(0, False, True, True)).decode(
                "utf-8"
            )
            self.len_name2 = self._io.read_u1()
            self.name2 = (self._io.read_bytes(self.len_name2)).decode("utf-8")

        class Flags(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.bool1 = self._io.read_bits_int_be(1) != 0
                self.num4 = self._io.read_bits_int_be(3)
                self.padding = self._io.read_bits_int_be(4)

        @property
        def num2(self):
            if hasattr(self, "_m_num2"):
                return self._m_num2

            self._m_num2 = (self.num2_hi << 16) | self.num2_lo
            return getattr(self, "_m_num2", None)


if __name__ == "__main__":
    import sys
    import timeit

    try:
        from rich import print
    except ImportError:
        pass

    with open(sys.argv[1], "rb") as fp:
        data = fp.read()

    time = timeit.timeit(lambda: Comparison1Kaitai.from_bytes(data), number=1000) / 1000
    print("[bold]Parsing measurements:[/]")
    print(f"[bold]default[/]  {time:.10f} sec/call")
