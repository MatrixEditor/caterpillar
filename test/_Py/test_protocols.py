# pyright: reportPrivateUsage=false
import pytest

from caterpillar.abc import (
    _ActionLike,
    _ArchLike,
    _ContextLambda,
    _ContextLike,
    _EndianLike,
    _OptionLike,
    _StructLike,
)
from caterpillar.py import (
    Aligned,
    BinaryExpression,
    Bitfield,
    Bytes,
    Chain,
    Compressed,
    Computed,
    ConditionalChain,
    Const,
    ConstBytes,
    ConstString,
    Context,
    ContextLength,
    ContextPath,
    CString,
    DigestField,
    DigestFieldAction,
    Dynamic,
    Encrypted,
    Enum,
    Field,
    Flag,
    Int,
    IPv4Address,
    IPv6Address,
    KeyCipher,
    Lazy,
    MACAddress,
    Memory,
    Pass,
    Pointer,
    Prefixed,
    PyStructFormattedField,
    RelativePointer,
    Sequence,
    String,
    Struct,
    SysNative,
    Transformer,
    UInt,
    UnaryExpression,
    Uuid,
    VarInt,
    system_arch,
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
    assert isinstance(obj, proto_ty), (
        f"Class {obj.__name__} does not conform to the {proto_ty.__name__} protocol"
    )
