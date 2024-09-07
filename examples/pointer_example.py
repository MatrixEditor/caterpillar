# type: ignore
from caterpillar._Py import (
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
    # Okay, this looks ugly, but it is only for demonstration purposes
    address: (uintptr * CString(...))[1]
    # the better way would be
    # address: Pointer(uintptr_fn, CString(...))[1]


data = b"\x00\x00\x00\x04Hello, World!\x00"
obj = unpack(Format, data, _arch=x86)
print(obj)
print(obj.address[0].get())
