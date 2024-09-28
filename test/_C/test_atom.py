# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar

if caterpillar.native_support():

    from caterpillar._C import atom, catom


    def test_atom_init():
        # Just verify that we can instantiate an atom
        atom()


    def test_catom_init():
        # Although, we can't do anything with this class, we can create
        # objects of  it, so let's test that.
        catom()


    def test_atom_inheritance():
        # Verify that we can inherit from atom and that catom
        # is a subclass of atom
        class Foo(atom):
            pass

        assert issubclass(Foo, atom)
        assert issubclass(catom, atom)


    def test_atom_methods():
        # Each method should throw a NotImplementedError
        a = atom()
        with pytest.raises(NotImplementedError):
            a.__pack__(None, None)

        with pytest.raises(NotImplementedError):
            a.__unpack__(None)

        # or return NotImplemented if not overridden
        assert a.__type__() == NotImplemented
