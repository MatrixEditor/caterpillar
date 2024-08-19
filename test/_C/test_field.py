# pylint: disable=unused-import,no-name-in-module,import-error
import pytest

import caterpillar

if caterpillar.native_support():

    from caterpillar._C import Field, fieldatom, atom
    from caterpillar._C import NATIVE_ENDIAN, HOST_ARCH, F_DYNAMIC


    def test_field_init():
        # Just verify that we can instantiate a field
        with pytest.raises(TypeError):
            Field()

        Field(atom())

        # use all parameters
        Field(
            atom(),
            name="foo",
            offset=1,
            length=2,
            endian=NATIVE_ENDIAN,
            default=3,
            switch={1: 2},
            condition=False,
            options=set(),
            arch=HOST_ARCH,
        )


    def test_field_offset():
        # The offset may be set using the constructor or by applying
        # the special '@' operator. We can apply a constant value or
        # a context lambda (callable function) here.
        assert Field(atom()).offset is None
        assert Field(atom(), offset=1).offset == 1
        assert (Field(atom()) @ 1).offset == 1
        assert (Field(atom()) @ (lambda ctx: 1)).offset(None) == 1


    def test_field_length():
        # The length may be set using the constructor or by applying
        # the special '[]' operation. Be aware, thatz multiple dimensions
        # are not supported yet.
        # The length can take the following types: int, ellipsis, slice
        # or a context lambda (callable function).
        field = Field(atom())
        assert field.length is None
        assert Field(atom(), length=1).length == 1
        assert field[1].length == 1
        assert field[lambda ctx: 1].length(None) == 1
        assert field[lambda x: 2 : :].length.start(None) == 2
        assert field[...].length is Ellipsis

        with pytest.raises(TypeError):
            # type not supported
            _ = field["foo"]


    def test_field_condition():
        # The condition is somewhat special as it will be deprecated in the
        # future. It may be a contant boolean value or a context lambda (callable
        # function). Use the '//' operatorto apply a new condition.
        field = Field(atom())
        assert field.condition is True  # the default value is True
        assert Field(atom(), condition=False).condition is False
        assert (field // (lambda ctx: False)).condition(None) is False
        assert (field // (lambda ctx: True)).condition(None) is True

        with pytest.raises(TypeError):
            # type not supported
            _ = field // "foo"


    def test_field_switch():
        # A switch can be defined using the '>>' operation and the
        # required value must be a dictionary or a context lambda.
        field = Field(atom())
        assert field.switch is None
        assert Field(atom(), switch={1: 2}).switch == {1: 2}

        with pytest.raises(TypeError):
            # type not supported
            _ = field >> "foo"

        # the stored value must be an atom instance, that can be
        # called directly.
        assert (field >> {1: atom()}).switch[1].__class__ == atom
        assert (field >> (lambda x: atom())).switch(None).__class__ == atom


    def test_field_options():
        # Options can be added with `|` and removed with `^`.
        field = Field(atom())
        assert len(field.options) == 1  # keep_pos is inferred
        assert F_DYNAMIC in (field | F_DYNAMIC).options
        assert F_DYNAMIC not in (field ^ F_DYNAMIC).options
