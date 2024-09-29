# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar
import enum
import typing

if caterpillar.native_support():

    from caterpillar._C import pack, unpack, computed, typeof

    def test_computed():
        value = 0xDEADBEEF
        # computed atoms don't affect the underlying stream
        assert unpack(b"", computed(value)) == 0xDEADBEEF
        assert unpack(b"", computed(lambda ctx: value)) == 0xDEADBEEF

    def test_computed_type():
        value = 0xDEADBEEF
        # Type will be inferred using the given value. A callable object
        # will use the Any type.
        assert typeof(computed(value)) == int
        assert typeof(computed(lambda ctx: value)) == typing.Any
