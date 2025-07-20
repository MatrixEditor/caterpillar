# pylint: disable=unused-import, no-name-in-module
import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar._C import Atom, LengthInfo

    def testc_atom_init():
        # instantiation will work but is useless
        atom = Atom()

        with pytest.raises(TypeError):
            _ = Atom(a=1)

    def testc_atom_protocol():
        # each method will raise NotImplementedError or
        # return NotImplemented
        atom = Atom()

        with pytest.raises(NotImplementedError):
            atom.__unpack__(None)

        with pytest.raises(NotImplementedError):
            atom.__pack__(None, None)

        with pytest.raises(NotImplementedError):
            atom.__unpack_many__(None, None)

        with pytest.raises(NotImplementedError):
            atom.__pack_many__(None, None, None)

        with pytest.raises(NotImplementedError):
            atom.__size__(None)

        assert atom.__type__() is NotImplemented
        assert atom.__bits__() is NotImplemented
