# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar
import enum
import typing

if caterpillar.native_support():

    from caterpillar._C import pack, unpack, lazy, typeof, u8

    def test_lazy():
        # Here, we can add a forward reference to types that may
        # appear after this line
        atom = lazy(lambda: u8)
        assert unpack(b"\x01", atom) == 1
        assert pack(1, atom) == b"\x01"

        # By default, the atom returned by the lambda funtion will be
        # cached internally. to prevent that, use always_lazy:
        atom = lazy(lambda: u8, always_lazy=True)
        assert unpack(b"\x01", atom) == 1
        assert unpack(b"\x01\x01\x01", atom[3]) == [1, 1, 1]

        # TODO: support pack_many
        # TODO: describe __repr__

    def test_lazy_type():
        atom = lazy(lambda: u8)
        assert typeof(atom) == int
