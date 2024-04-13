# pylint: disable=import-error,no-name-in-module
from caterpillar._core import (
    CpFieldAtom,
    pack_into,
    CpLayer,
    unpack,
    CpStruct,
    CpField,
    S_REPLACE_TYPES,
    CpAtom,
    pack
)
from io import BytesIO
import pytest


class Foo(CpFieldAtom):
    def __pack__(self, obj, layer: CpLayer):
        layer.state.write(obj.to_bytes(1, "big"))

    def __unpack__(self, layer: CpLayer):
        print(layer.obj, type(layer.obj))
        print(layer.path)
        return layer.state.read(1)[0]


class Bar:
    foo: Foo()

# x = CpStruct(Bar, alter_model=True)

# data = b"\x01" * 2
# with BytesIO(data) as stream:
#     val = unpack(stream, x[Foo()::])
#     print(val)




class IntFormat4:
    foo: Foo()
    bar: Foo()


IntFormat4_Struct = CpStruct(IntFormat4, alter_model=True)
import sys
def test_struct_unpack():
    f = IntFormat4_Struct[2]
    assert f.length == 2
    print(sys.getrefcount(f))
    result = pack([IntFormat4(1, 1), IntFormat4(2, 2)], f)
    print(f, sys.getrefcount(f), result)
    print(unpack(result, IntFormat4_Struct[...]))

test_struct_unpack()