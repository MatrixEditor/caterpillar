# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar
import enum

if caterpillar.native_support():

    from caterpillar._C import enumeration, pack, unpack, u8

    def test_enum():
        # TODO: The Struct class should infer the enum
        # type automatically.
        class TestEnum(enum.Enum):
            A = 1
            B = 2
            C = 3

        # We can use an enumeration atom to parse data and translate
        # it to an enum value. By default, invalid values won't get
        # reported (TODO: strict parsing flag)
        enum_atom = enumeration(u8, TestEnum)
        assert unpack(b"\x01", enum_atom) == TestEnum.A
        assert pack(TestEnum.B, enum_atom) == b"\x02"

        # NOTE: byteorder operations will be delegated to the underlying
        # atom.