# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar

if caterpillar.native_support():

    from caterpillar.c import atom, Struct, struct, TYPE_MAP, u8, pack


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
        assert s.members["a"].default == 1


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

    def test_struct_decorator():
        @struct
        class Foo:
            a: atom() = 1

        assert len(Foo.__struct__.members) == 1
        assert Foo().a == 1

    def test_struct_type_handler():
        TYPE_MAP[int] = u8

        @struct
        class Format:
            a: int

        assert len(Format.__struct__.members) == 1
        assert Format(1).a == 1
        assert pack(Format(1), Format.__struct__) == b"\x01"

    def test_struct_inheritance():
        @struct
        class Foo:
            a: atom() = 1

        @struct
        class Bar(Foo):
            b: atom() = 2

        assert len(Bar.__struct__.members) == 2
        assert Bar().a == 1
        assert Bar().b == 2