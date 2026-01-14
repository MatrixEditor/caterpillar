# type: ignore
from caterpillar.py import struct, pack, unpack, uint8
from caterpillar.shortcuts import f

try:
    from rich import print
except ImportError:
    pass


@struct
class Format:
    value: f[int, uint8]
    inner: f[dict[str, int], {"a": uint8, "b": uint8}]


obj = Format(value=1, inner={"a": 2, "b": 3})
data = pack(obj)
print(data)
deobj: Format = unpack(Format, data)
print(deobj)
# Context instance, which is a dict under the hood
print(type(deobj.inner))
