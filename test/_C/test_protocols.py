# pyright: reportPrivateUsage=false
import pytest

from caterpillar.c import (
    c_Arch,
    c_Context,
    c_Endian,
    c_Option,
    AtOffset,
    Atom,
    BuiltinAtom,
    Conditional,
    Repeated,
    Switch
)
from caterpillar.abc import (
    _StructLike,
    _OptionLike,
    _EndianLike,
    _ArchLike,
    _ContextLike,
)


# === PROTOCOL COMPLIANCE ===
# All tests below should verify the protocol compliance of all classes
# defined in this library. New ones should be added here too.
@pytest.mark.parametrize(
    ("obj", "proto_ty"),
    [
        # _StructLike
        (Atom, _StructLike),
        (BuiltinAtom, _StructLike),
        (Repeated, _StructLike),
        (AtOffset, _StructLike),
        (Switch, _StructLike),
        (Conditional, _StructLike),
        # _OptionLike
        (c_Option, _OptionLike),
        # _EndianLike
        (c_Endian, _EndianLike),
        # _ArchLike
        (c_Arch, _ArchLike),
        # _ContextLike
        (c_Context, _ContextLike),
    ],
)
def test_py_protocol(obj: type, proto_ty: type) -> None:
    assert isinstance(
        obj, proto_ty
    ), f"Class {obj.__name__} does not conform to the {proto_ty.__name__} protocol"
