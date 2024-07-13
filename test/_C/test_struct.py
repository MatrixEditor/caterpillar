# pylint: disable=unused-import,no-name-in-module,import-error
import pytest

from caterpillar._C import atom, Struct


def test_struct_init():
    # Just verify that we can instantiate a struct
    with pytest.raises(TypeError):
        Struct()

    with pytest.raises(TypeError):
        Struct(atom())


def test_struct_model():
    # The struct's model must be a type
    class Foo:
        a: atom() = 1

    s = Struct(Foo)
    assert len(s.members) == 1
    assert s.model is Foo
    # The member dictionary will store Field instances,
    # which then store the default value
    assert s.members["a"].field.default == 1


def test_invalid_struct_model():
    # invalid types will be reported using a ValuError
    class Foo:
        a: int

    with pytest.raises(ValueError):
        Struct(Foo)


def test_struct_altered_model():
    # IF specified, the struct will inspect the given
    # type AND inject a custom constructor.
    class Foo:
        a: atom() = 1

    s = Struct(Foo, alter_model=True)
    assert len(s.members) == 1
    # As the attribute 'a' defines a default value, we can
    # create a new instance without the need of passing a
    # value for 'a'.
    assert Foo().a == 1
    assert Foo(a=2).a == 2
