from caterpillar.abc import ContextLike
from caterpillar.byteorder import Inherit
from caterpillar.context import SetContextVar
from caterpillar.fields import Field
from caterpillar.py import (
    CTX_ORDER,
    BigEndian,
    Dynamic,
    DynByteOrder,
    Invisible,
    LittleEndian,
    Pointer,
    Prefixed,
    bitfield,
    ctx,
    f,
    pack,
    parent,
    struct,
    this,
    uint8,
    uint16,
    uint32,
    uint64,
    unpack,
    StructDefMixin,
)
from caterpillar.types import uint8_t, uint16_t, uint32_t, uint64_t


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
    def byteorder_func(context: ContextLike):  # pyright: ignore[reportUnusedParameter]
        # custom implementation...
        return LittleEndian

    @struct(order=BigEndian)
    class Format:
        a: uint16_t
        # --- All fields below use the dynamic byteorder if annotated
        #     with Dynamic
        _spec: f[None, SetContextVar(CTX_ORDER, byteorder_func)] = Invisible()
        b: f[int, Dynamic(ctx._order) + uint32]

    obj = Format(a=0x1234, b=0x56789ABC)
    data = pack(obj)
    assert data.hex() == "1234bc9a7856"


def test_dyn_byteorder_grandparent_context():
    @struct(order=Dynamic(parent.parent.value))
    class Inner:
        value: uint32_t

    @struct
    class Middle:
        inner: Inner

    @struct
    class Outer:
        value: uint8_t
        middle: Middle

    big_endian = Outer(0, Middle(Inner(0x11223344)))
    little_endian = Outer(1, Middle(Inner(0x11223344)))

    big_data = bytes.fromhex("0011223344")
    little_data = bytes.fromhex("0144332211")
    assert pack(big_endian) == big_data
    assert unpack(Outer, big_data) == big_endian
    assert pack(little_endian) == little_data
    assert unpack(Outer, little_data) == little_endian


def test_inherit_byteorder_struct():
    # order=Inherit makes a struct resolve its own byte order from
    # whichever struct embeds it, instead of a fixed order.
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    @struct(order=BigEndian)
    class Outer:
        inner: Inner

    @struct(order=LittleEndian)
    class Format:
        inner: Inner

    data = bytes.fromhex("11223344")
    assert unpack(Outer, data).inner.value == 0x11223344
    assert pack(Outer(Inner(0x11223344))) == data

    assert unpack(Format, data).inner.value == 0x44332211
    assert pack(Format(Inner(0x44332211))) == data


def test_inherit_byteorder_standalone_fallback():
    # A struct declared with order=Inherit but used without an enclosing
    # struct (e.g. passed directly to pack/unpack) falls back to the
    # regular default byte order, exactly like order=None.
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    data = bytes.fromhex("11223344")
    assert unpack(Inner, data).value == 0x44332211  # little-endian default
    assert pack(Inner(0x44332211)) == data


def test_inherit_byteorder_sibling():
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    @struct
    class Format:
        little: LittleEndian + Inner
        big: BigEndian + Inner

    data = bytes.fromhex("11223344") * 2
    obj = unpack(Format, data)
    assert obj.little.value == 0x44332211
    assert obj.big.value == 0x11223344
    assert pack(obj) == data


def test_inherit_byteorder_mix():
    @struct(order=Inherit)
    class Inner(StructDefMixin):
        value: uint32_t

    @struct(order=BigEndian)
    class Outer:
        little: LittleEndian + Inner
        big: BigEndian + Inner
        inherited: Inner  # follows Outer's own order (BigEndian)

    data = bytes.fromhex("11223344") * 3
    obj = unpack(Outer, data)
    assert obj.little.value == 0x44332211
    assert obj.big.value == 0x11223344
    assert obj.inherited.value == 0x11223344
    assert pack(obj) == data

    # Flipping the parent's own order only moves the plain reference;
    # the two explicit overrides stay pinned to their declared order.
    @struct(order=LittleEndian)
    class Format:
        little: LittleEndian + Inner
        big: BigEndian + Inner
        inherited: Inner  # now follows Format's LittleEndian

    obj = unpack(Format, data)
    assert obj.little.value == 0x44332211
    assert obj.big.value == 0x11223344
    assert obj.inherited.value == 0x44332211
    assert pack(obj) == data


def test_inherit_byteorder_array():
    # order=Inherit resolves the same way for array members.
    @struct(order=Inherit)
    class Inner(StructDefMixin):
        value: uint32_t

    @struct(order=BigEndian)
    class Outer:
        items: Inner[2]

    data = bytes.fromhex("11223344") * 2
    obj = unpack(Outer, data)
    assert [item.value for item in obj.items] == [0x11223344, 0x11223344]
    assert pack(obj) == data


def test_inherit_byteorder_chain():
    # Multi-level Inherit chains resolve:
    # Outer(BigEndian) -> Middle(Inherit) -> Inner(Inherit)
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    @struct(order=Inherit)
    class Middle:
        inner: Inner

    @struct(order=BigEndian)
    class Outer:
        middle: Middle

    data = bytes.fromhex("11223344")
    obj = unpack(Outer, data)
    assert obj.middle.inner.value == 0x11223344
    assert pack(obj) == data


def test_inherit_byteorder_mixed_chain():
    # A chain that mixes explicit orders and Inherit at different depths must
    # resolve each Inherit level against the *nearest* concrete ancestor,
    # not the outermost one: Outer(BE) -> Middle(LE, explicit) -> Inner(Inherit)
    # Inner must follow Middle's LE, not Outer's BE.
    @struct(order=Inherit)
    class Inner:
        v: uint32_t

    @struct(order=LittleEndian)
    class Middle:
        v: Inner

    @struct(order=BigEndian)
    class Outer:
        v: Middle

    data = bytes.fromhex("11223344")
    obj = unpack(Outer, data)
    assert obj.v.v.v == 0x44332211
    assert pack(obj) == data


def test_inherit_byteorder_prefixed():
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    @struct(order=BigEndian)
    class Outer:
        inner: Prefixed(uint8, Inner)

    obj = Outer(Inner(0x11223344))
    packed = pack(obj)
    assert packed == bytes.fromhex("04") + bytes.fromhex("11223344")
    assert unpack(Outer, packed).inner.value == 0x11223344


def test_inherit_byteorder_explicit_inner_order():
    @struct(order=LittleEndian)
    class Inner:
        value_le: uint64_t

    @struct(order=BigEndian)
    class Format:
        inner: Inner

    value = 0x123456789ABCDEF
    raw_le = bytes.fromhex("efcdab8967452301")
    obj = Format(Inner(value))
    assert pack(obj) == raw_le
    assert unpack(Format, raw_le) == obj


def test_inherit_byteorder_annotated_override():
    # f[...] annotations can override the order for a single field, just
    # like they already do for plain atoms (see test_byteorder_struct_explicit).
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    @struct(order=BigEndian)
    class Outer:
        a: f[Inner, Inner, LittleEndian]

    data = bytes.fromhex("11223344")
    assert unpack(Outer, data).a.value == 0x44332211


def test_inherit_byteorder_bitfield():
    # Bitfield supports order=Inherit exactly like a regular struct.
    @bitfield(order=Inherit)
    class Inner:
        a: f[int, 5]
        b: f[int, 7]

    @struct(order=BigEndian)
    class Outer:
        bits: Inner

    @struct(order=LittleEndian)
    class Format:
        bits: Inner

    obj = Inner(a=0b10101, b=0b1100110)
    data_be = bytes.fromhex("ae60")
    data_le = bytes.fromhex("60ae")

    assert pack(Outer(obj)) == data_be
    assert unpack(Outer, data_be).bits == obj

    assert pack(Format(obj)) == data_le
    assert unpack(Format, data_le).bits == obj


def test_inherit_byteorder_prefixed_nested_bitfield():
    # An explicitly ordered length field must not become the embedding order
    # for a deeply nested Inherit payload.
    @bitfield(order=Inherit)
    class InnerBits:
        value: f[int, 16]

    @struct(order=Inherit)
    class Inner:
        bits: InnerBits

    @struct(order=BigEndian)
    class Outer:
        inner: Prefixed(LittleEndian + uint16, Inner)

    data = bytes.fromhex("02001122")
    obj = unpack(Outer, data)
    assert obj.inner.bits.value == 0x1122
    assert pack(Outer(Inner(InnerBits(0x1122)))) == data


def test_inherit_byteorder_pointer_target_after_ordered_pointer():
    # The pointer representation can have its own order without changing the
    # order inherited by the object it points to.
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    @struct(order=BigEndian)
    class Outer:
        inner: Pointer(LittleEndian + uint16, Inner)

    data = bytes.fromhex("020011223344")
    obj = unpack(Outer, data)
    assert obj.inner.obj.value == 0x11223344

    obj.inner.obj = Inner(0x11223344)
    assert pack(obj) == data


def test_inherit_byteorder_switch_restores_embedding_field():
    @struct(order=Inherit)
    class Inner:
        value: uint32_t

    discriminator = Field(LittleEndian + uint16, options={1: Inner})

    @struct(order=BigEndian)
    class Format:
        inner: discriminator

    @struct(order=BigEndian)
    class Outer:
        inner: Field(lambda _context: 1, options={1: Inner})

    assert unpack(Format, bytes.fromhex("010011223344")).inner.value == 0x11223344
    assert unpack(Outer, bytes.fromhex("11223344")).inner.value == 0x11223344
