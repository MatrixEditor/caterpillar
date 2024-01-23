from caterpillar.shortcuts import *
from caterpillar.fields import uint8, Field

try:
    from rich import print
except ImportError:
    pass


@struct
class Format:
    value: uint8
    inner: {"a": uint8, "b": uint8}


obj = Format(value=1, inner={"a": 2, "b": 3})
data = pack(obj)
print(data)
deobj: Format = unpack(Format, data)
print(deobj)
print(type(deobj.inner))  # Context instance
