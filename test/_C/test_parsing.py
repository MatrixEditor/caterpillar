# pylint: disable=unused-import,no-name-in-module,import-error
import typing
import pytest
import caterpillar

if caterpillar.native_support():

    from caterpillar._C import atom, typeof, sizeof, patom, repeated
    from caterpillar._C import switch
    from caterpillar._C import unpack, layer, Struct, pack, ContextPath


    # This atom class will only be able to return its associated
    # type.
    class Foo(atom):
        def __type__(self):
            return str


    # Using the base class 'patom' enabled direct field creation
    # using the common operators.
    class Bar(patom):
        def __size__(self, ctx):
            return 2


    # Only packing is implemented
    class Baz(patom):
        def __unpack__(self, ctx: layer):
            return int.from_bytes(ctx.state.read(2))

        def __pack__(self, obj, ctx: layer):
            ctx.state.write(obj.to_bytes(2, "big"))


    def test_typeof():
        # The default behaviour is to call __type__ on the given
        # atom. Note that typing.Optional is not supported yet and
        # therefore it won't be placed if a condition as assigned
        # to a field.
        f = Foo()
        assert typeof(f) == str

        # That will change if we have a field with a length or a
        # switch statement.
        field = repeated(f, 2)
        assert typeof(field) == typing.List[str]

        field2 = switch(f, {1: atom()})[2]
        # We can't know the type of a switch atom which does
        # not implement the __type__ method
        assert typeof(atom()) == typing.Any
        assert typeof(field2) == typing.List[typing.Any]
        # switch and length can be combined as well
        assert typeof(field2[2]) == typing.List[typing.List[typing.Any]]


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
        with pytest.raises(TypeError):
            sizeof(field >> {2: Bar()})

        # Calculation is done by first evaluating the length of
        # the field's atom and then multiply the length of the evalutated
        # switch atom by the field's length.
        # REVISIT: switch atoms does not have a static size
        with pytest.raises(TypeError):
            field = switch(b, (lambda ctx: Bar()))[2]
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
        # assert unpack(data, Field(b) >> {1: b}) == 2
        assert unpack(data, b @ 0x0002) == 2


    def test_unpack_struct():
        # In order to unpack structs, we first need a class definition
        # with a constructor addressing all defined fields.
        data = b"\x00\x01\x00\x02"

        class SFoo:
            a: Baz()
            b: Baz()

            # REVISIT: maybe provide a default implementation
            def __eq__(self, other):
                return self.a == other.a and self.b == other.b

        # Simply create the struct using the class definition
        s = Struct(SFoo, alter_model=True)
        assert unpack(data, s) == SFoo(a=1, b=2)


    def test_unpack_struct_cp():
        # CASE: a struct definition with an array of data, which
        # length is computed by a context lambda.
        cp = ContextPath("obj.a")
        data = b"\x00\x01\x00\x02"

        class SFoo:
            a: Baz()
            b: Baz()[cp]

            # REVISIT: maybe provide a default implementation
            def __eq__(self, other):
                return self.a == other.a and self.b == other.b

        # Simply create the struct using the class definition
        s = Struct(SFoo, alter_model=True)
        assert unpack(data, s) == SFoo(a=1, b=[2])


    def test_pack_basic():
        # The packing will be done by calling __pack__ on the
        # target atom.
        b = Baz()
        # Same as in test_unpack_basic
        assert pack(1, b) == b"\x00\x01"
        assert pack([1, 2], b[2]) == b"\x00\x01\x00\x02"
        assert pack([2], b[b::]) == b"\x00\x01\x00\x02"
        assert pack(2, b @ 0x0002) == b"\x00\x00\x00\x02"


    def test_pack_struct():
        # Same scheme as described in test_unpack_struct
        class SBar:
            a: Baz()
            b: Baz()

        s = Struct(SBar, alter_model=True)
        assert pack(SBar(a=1, b=2), s) == b"\x00\x01\x00\x02"


    def test_pack_struct_cp():
        # CASE: a struct definition with an array of data, which
        # length is computed by a context lambda.
        cp = ContextPath("obj.a")

        # The next class for illustrating the use of context
        # lambdas. Please use Baz()[Baz()::] as a shortcut.
        class SBaz:
            a: Baz()  # the length of the following field
            b: Baz()[cp]  # obj.a is evaluated before packing
            # the data

        s = Struct(SBaz, alter_model=True)
        assert pack(SBaz(a=1, b=[2]), s) == b"\x00\x01\x00\x02"
