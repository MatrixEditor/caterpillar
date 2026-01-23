# pyright: reportPrivateUsage=false
import pytest

from caterpillar.py import (
    BinaryExpression,
    Bitfield,
    Chain,
    Compressed,
    ConditionalChain,
    ConstBytes,
    ConstString,
    ContextLength,
    ContextPath,
    DigestField,
    DigestFieldAction,
    Encrypted,
    Enum,
    Field,
    IPv4Address,
    IPv6Address,
    Int,
    KeyCipher,
    Lazy,
    MACAddress,
    Pointer,
    PyStructFormattedField,
    RelativePointer,
    Sequence,
    Struct,
    SysNative,
    Const,
    Dynamic,
    Transformer,
    UInt,
    Flag,
    UnaryExpression,
    VarInt,
    system_arch,
    Context,
    String,
    Bytes,
    Memory,
    Computed,
    Pass,
    CString,
    Prefixed,
    Uuid,
    Aligned,
)
from caterpillar.abc import (
    _StructLike,
    _OptionLike,
    _EndianLike,
    _ArchLike,
    _ContextLike,
    _ContextLambda,
    _ActionLike,
)


# === PROTOCOL COMPLIANCE ===
# All tests below should verify the protocol compliance of all classes
# defined in this library. New ones should be added here too.
# TODO: include types from _C module here
@pytest.mark.parametrize(
    ("obj", "proto_ty"),
    [
        # _StructLike
        (Const, _StructLike),
        (PyStructFormattedField, _StructLike),
        (Field, _StructLike),
        (ConstBytes, _StructLike),
        (ConstString, _StructLike),
        (Enum, _StructLike),
        (String, _StructLike),
        (Bytes, _StructLike),
        (Memory, _StructLike),
        (Computed, _StructLike),
        (Pass, _StructLike),
        (CString, _StructLike),
        (Prefixed, _StructLike),
        (Int, _StructLike),
        (UInt, _StructLike),
        (Uuid, _StructLike),
        (Aligned, _StructLike),
        (VarInt, _StructLike),
        (Compressed, _StructLike),
        (Encrypted, _StructLike),
        (KeyCipher, _StructLike),
        (MACAddress, _StructLike),
        (IPv4Address, _StructLike),
        (IPv6Address, _StructLike),
        (Pointer, _StructLike),
        (RelativePointer, _StructLike),
        (ConditionalChain, _StructLike),
        (DigestField, _StructLike),
        (Lazy, _StructLike),
        (Chain, _StructLike),
        (Transformer, _StructLike),
        (Struct, _StructLike),
        (Sequence, _StructLike),
        (Bitfield, _StructLike),
        # _OptionLike
        (Flag("_"), _OptionLike),
        # _EndianLike
        (SysNative, _EndianLike),
        (Dynamic, _EndianLike),
        # _ArchLike
        (system_arch, _ArchLike),
        # _ContextLike
        (Context, _ContextLike),
        # _ContextLambda
        (ContextPath, _ContextLambda),
        (ContextLength, _ContextLambda),
        (UnaryExpression, _ContextLambda),
        (BinaryExpression, _ContextLambda),
        # _ActionLike,
        (DigestFieldAction, _ActionLike),
    ],
)
def test_py_protocol(obj: type, proto_ty: type) -> None:
    assert isinstance(
        obj, proto_ty
    ), f"Class {obj.__name__} does not conform to the {proto_ty.__name__} protocol"
