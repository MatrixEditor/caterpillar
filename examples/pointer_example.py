# type: ignore
from caterpillar.fields import pointer
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
from caterpillar.shortcuts import f
from caterpillar.fields.pointer import uintptr_fn
from caterpillar.abc import _StructLike
try:
    from rich import print
except ImportError:
    pass

set_struct_flags(S_REPLACE_TYPES)

@struct(kw_only=False, order=BigEndian)
class Format:
    address: f[pointer[str], uintptr * CString(...)]


data = b"\x00\x00\x00\x04Hello, World!\x00"
obj = unpack(Format, data, _arch=x86)
print(obj)
print(obj.address.get())
