import typing

from caterpillar.byteorder import Dynamic, DynByteOrder, BigEndian, LittleEndian
from caterpillar.py import struct, pack, uint64, unpack, uint16, uint32
from caterpillar.types import uint16_t, uint32_t, uint64_t, uint8_t
from caterpillar.context import CTX_ORDER, SetContextVar, ctx, this
from caterpillar.shortcuts import f
from caterpillar.abc import _ContextLike  # pyright: ignore[reportPrivateUsage]


def test_byteorder_pack_explicit():
    value = 0x123456789ABCDEF
    raw_le = bytes.fromhex("efcdab8967452301")
    raw_be = bytes.fromhex("0123456789abcdef")

    # 1. explicit use of byteorder without a @struct type
    assert pack(value, uint64, order=LittleEndian) == raw_le
    assert pack(value, uint64, order=BigEndian) == raw_be
    assert unpack(uint64, raw_be, order=BigEndian) == value
    assert unpack(uint64, raw_le, order=LittleEndian) == value
    # sanity check
    assert unpack(uint64, raw_le, order=BigEndian) != value


def test_byteorder_pack_struct_implicit():
    value = 0x123456789ABCDEF
    raw_le = bytes.fromhex("efcdab8967452301")

    # 2 implicit use of byteorder in a @struct type
    @struct(order=LittleEndian)
    class Format:
        value_le: uint64_t

    obj = Format(value_le=value)
    assert pack(obj) == raw_le
    assert unpack(Format, raw_le) == obj


def test_byteorder_struct_explicit():
    value = 0x123456789ABCDEF
    raw_le = bytes.fromhex("efcdab8967452301")
    raw_be = bytes.fromhex("0123456789abcdef")

    # 3. explicit use of byteorder in a @struct type
    @struct(order=LittleEndian)
    class Format:
        value_le: uint64_t
        # fields with an endian already set, won't be affected
        # by the change in @struct(...)
        value_be: f[int, uint64, BigEndian]

    obj = Format(value, value)
    assert pack(obj) == raw_le + raw_be
    assert pack(obj) != raw_be + raw_le
    assert unpack(Format, raw_le + raw_be) == obj
    assert unpack(Format, raw_be + raw_le) != obj


def test_byteorder_struct_inner():
    value = 0x123456789ABCDEF
    raw_le = bytes.fromhex("efcdab8967452301")

    # 4. Inner types / referenced types
    @struct(order=LittleEndian)
    class Inner:
        # endian is set to 'little'
        value_le: uint64_t

    @struct(order=BigEndian)
    class Format:
        # even though BigEndian is applied here,
        # the inner struct already defines little
        inner: Inner

    obj = Format(Inner(value))
    assert pack(obj) == raw_le
    assert unpack(Format, raw_le) == obj


def test_dyn_byteorder_pack():
    # Dynamic byteorder without any other configuration
    # uses the _order value from the root context
    @struct(order=Dynamic)
    class Format:
        a: uint16_t
        b: uint32_t

    obj = Format(a=0x1234, b=0x56789ABC)

    # 1. Pack with BigEndian
    data_be = pack(obj, order=BigEndian)

    # 2. Pack with LittleEndian
    data_le = pack(obj, order=LittleEndian)

    # data must be different for each endian
    assert data_be != data_le


def test_dyn_byteorder_unpack():
    # Dynamic byteorder without any other configuration
    # uses the _order value from the root context
    @struct(order=Dynamic)
    class Format:
        a: uint8_t
        b: uint16_t

    # Prepare data in BigEndian format
    obj_be = Format(a=0x12, b=0x3456)
    data_be = pack(obj_be, order=BigEndian)

    # Unpack with BigEndian
    unpacked_be = unpack(Format, data_be, order=BigEndian)
    assert unpacked_be.a == 0x12
    assert unpacked_be.b == 0x3456

    # Unpack with LittleEndian
    unpacked_le = unpack(Format, data_be, order=LittleEndian)
    assert unpacked_le.a == 0x12
    assert unpacked_le.b != 0x3456  # Value should differ due to endian change


def test_dyn_byteorder_key():
    # dynamic byteorder allows specifying a key to get the
    # byteorder from the context
    @struct(order=Dynamic(this.spec), kw_only=True)
    class Format:
        # The target context value can be either a string containing
        # the endian format character, a ByteOrder object or any value
        # convertible to boolean (True=LittleEndian, False=BigEndian)
        spec: uint8_t = 0
        a: uint16_t
        b: uint32_t

    obj_be = Format(spec=0, a=0x1234, b=0x56789ABC)
    obj_le = Format(spec=1, a=0x1234, b=0x56789ABC)
    assert pack(obj_be)[1:] != pack(obj_le)[1:]  # skip spec byte for comparison


def test_dyn_byteorder_func():
    # dynamic byteorder allows specifying a function to determine
    # the byteorder at runtime
    def byteorder_func():
        # custom code ...
        return BigEndian

    @struct(order=DynByteOrder(func=byteorder_func))
    class Format:
        a: uint16_t
        b: uint32_t

    obj = Format(a=0x1234, b=0x56789ABC)
    data = pack(obj)
    assert data.hex() == "123456789abc"


def test_dyn_byteorder_mixed():
    # dynamic byteorder can also be applied to one field at a time
    # instead of all fields within a struct
    @struct(order=BigEndian, kw_only=True)
    class Format:
        spec: uint8_t = 0
        a: f[int, DynByteOrder(key=this.spec) + uint16]
        # alternatively
        # a: Dynamic(this.spec) + uint16
        b: uint32_t

    obj = Format(spec=0, a=0x1234, b=0x56789ABC)
    data_be = pack(obj)
    obj.spec = 1
    data_le = pack(obj)
    assert data_be[1:] != data_le[1:]


def test_dyn_byteorder_action():
    # byteorder based on a custom pre-computed context value
    def byteorder_func(context: _ContextLike):  # pyright: ignore[reportUnusedParameter]
        # custom implementation...
        return LittleEndian

    @struct(order=BigEndian)
    class Format:
        a: uint16_t
        # --- All fields below use the dynamic byteorder if annotated
        #     with Dynamic
        if not typing.TYPE_CHECKING:
            _spec: SetContextVar(CTX_ORDER, byteorder_func)
        b: f[int, Dynamic(ctx._order) + uint32]

    obj = Format(a=0x1234, b=0x56789ABC)
    data = pack(obj)
    assert data.hex() == "1234bc9a7856"
