# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import typing

from caterpillar._core import atom, typeof, Field, sizeof, fieldatom
from caterpillar._core import unpack, layer


# This atom class will only be able to return its associated
# type.
class Foo(atom):
    def __type__(self):
        return str


# Using the base class 'fieldatom' enabled direct field creation
# using the common operators.
class Bar(fieldatom):
    def __size__(self, ctx):
        return 2


# Only packing is implemented
class Baz(fieldatom):
    def __unpack__(self, ctx: layer):
        return int.from_bytes(ctx.state.read(2))


def test_typeof():
    # The default behaviour is to call __type__ on the given
    # atom. Note that typing.Optional is not supported yet and
    # therefore it won't be placed if a condition as assigned
    # to a field.
    f = Foo()
    assert typeof(f) == str

    # That will change if we have a field with a length or a
    # switch statement.
    field = Field(f, length=2)
    assert typeof(field) == typing.List[str]

    field2 = Field(f, switch={1: atom()})
    with pytest.raises(NotImplementedError):
        # We can't know the type of a switch atom which does
        # not implement the __type__ method
        _ = typeof(field2)

    field2.switch[2] = Foo()
    assert typeof(field2) == typing.Union[str]

    # switch and length can be combined as well
    assert typeof(field2[2]) == typing.List[typing.Union[str]]


def test_sizeof():
    # The size will be calculated according to the value
    # returned by __size__ on the given atom.
    b = Bar()
    assert sizeof(b) == 2

    # The size will be multplied by the length of the field
    field = b[4]
    assert sizeof(field) == 2 * 4

    # NOTE: A switch context is somewhat special as we don't
    # know the target atom yet. Therefore, only context lambdas
    # as switch values are supported.
    with pytest.raises(ValueError):
        sizeof(field >> {2: Bar()})

    # Calculation is done by first evaluating the length of
    # the field's atom and then multiply the length of the evalutated
    # switch atom by the field's length.
    field = Field(b, length=2, switch=(lambda ctx: Bar()))
    assert sizeof(field) == 2 + (2 * 2)


def test_unpack_basic():
    # The unpacking will be done by calling __unpack__ on the
    # target atom.
    data = b"\x00\x01\x00\x02"
    b = Baz()
    # Either we use the atom directly or encapsulate it in a
    # field instance.
    assert unpack(data, b) == 1
    assert unpack(data, b[2]) == [1, 2]
    # NOTE: the next expression might look a little bit wierd, but
    # is essentially defines a prefixed collection of Baz atoms.
    assert unpack(data, b[b::]) == [2]
    # NOTE: parsing is done by first unpacking the switch value (Baz
    # atom) and then use it aas the key of the switch dictionary. the
    # returned atom will be used to parse the rest of the data.
    assert unpack(data, b >> {1: b}) == 2
    assert unpack(data, b @ 0x0002) == 2
