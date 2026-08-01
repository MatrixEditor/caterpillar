from typing_extensions import Generic, TypeVar

from caterpillar.py import (
    BigEndian,
    derive,
    f,
    field_of,
    pack,
    struct,
    template,
    uint8,
    uint16,
    unpack,
)
from caterpillar.types import uint8_t


def test_generic_template_direct_typevar():
    T = TypeVar("T")

    @template
    class Box(Generic[T]):
        value: T

    # When we use the struct candidate directly, type checkers won't be able to
    # infer the right type, since these structs are of type 'PyStructFormattesField'
    # and not 'int'. Use the f[int, <struct>> expression instead.
    ByteBox = Box[uint8]

    assert ByteBox is Box[uint8]
    assert ByteBox.__origin__ is Box
    assert ByteBox.__args__ == (uint8,)
    assert pack(ByteBox(7)) == b"\x07"
    assert unpack(ByteBox, b"\x08") == ByteBox(8)
    assert pack([ByteBox(1), ByteBox(2)], ByteBox[2]) == b"\x01\x02"


def test_generic_template_direct_typevar_annotated_field():
    T = TypeVar("T")

    @template
    class Box(Generic[T]):
        value: T

    ByteBox = Box[uint8_t]

    assert ByteBox is Box[uint8_t]
    assert ByteBox.__origin__ is Box
    assert ByteBox.__args__ == (uint8_t,)
    assert pack(ByteBox(7)) == b"\x07"
    assert unpack(ByteBox, b"\x08") == ByteBox(8)
    assert pack([ByteBox(1), ByteBox(2)], ByteBox[2]) == b"\x01\x02"


def test_generic_template_multiple_typevars():
    T = TypeVar("T")
    U = TypeVar("U")

    @template
    class Pair(Generic[T, U]):
        left: T
        right: U

    ByteWordPair = Pair[uint8, uint16]
    obj = ByteWordPair(1, 0x0203)

    assert pack(obj, order=BigEndian) == b"\x01\x02\x03"
    assert unpack(ByteWordPair, b"\x01\x02\x03", order=BigEndian) == obj


def test_generic_template_field_of():
    T = TypeVar("T")

    @template
    class Vector(Generic[T]):
        values: f[list[T], field_of(T)[2]]

    # hint: use the *_t types directly when you use type checkers
    ByteVector = Vector[uint8_t]
    obj = ByteVector([3, 4])

    assert ByteVector.__annotations__["values"].__args__[0] == list[object]
    assert pack(obj) == b"\x03\x04"
    assert unpack(ByteVector, b"\x05\x06") == ByteVector([5, 6])


def test_generic_template_derive():
    T = TypeVar("T")

    @template
    class Box(Generic[T]):
        value: T

    ByteBox = derive(Box, uint8, name="DerivedGenericByteBoxForTest")
    assert derive(ByteBox) is ByteBox

    @struct
    class Packet(ByteBox):
        tail: f[int, uint16]

    obj = Packet(1, 0x0203)

    assert pack(obj, order=BigEndian) == b"\x01\x02\x03"
    assert unpack(Packet, b"\x04\x05\x06", order=BigEndian) == Packet(4, 0x0506)
