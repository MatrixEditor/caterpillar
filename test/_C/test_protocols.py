# pyright: reportPrivateUsage=false
import pytest

import caterpillar

if caterpillar.native_support():
    from caterpillar.abc import (
        _ArchLike,
        _ContextLike,
        _EndianLike,
        _OptionLike,
        _StructLike,
    )
    from caterpillar.c import (
        AtOffset,
        Atom,
        BuiltinAtom,
        Conditional,
        Repeated,
        Switch,
        c_Arch,
        c_Context,
        c_Endian,
        c_Option,
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
        assert isinstance(obj, proto_ty), (
            f"Class {obj.__name__} does not conform to the {proto_ty.__name__} protocol"
        )
