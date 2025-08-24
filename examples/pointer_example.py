# type: ignore
from caterpillar.py import (
    set_struct_flags,
    uintptr,
    CString,
    BigEndian,
    S_REPLACE_TYPES,
    unpack,
    struct,
    x86
)
from caterpillar.fields.pointer import uintptr_fn

try:
    from rich import print
except ImportError:
    pass

set_struct_flags(S_REPLACE_TYPES)


@struct(kw_only=False, order=BigEndian)
class Format:
    address: uintptr * CString(...)


data = b"\x00\x00\x00\x04Hello, World!\x00"
obj = unpack(Format, data, _arch=x86)
print(obj)
print(obj.address.get())
