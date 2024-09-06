# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar._C import unpack, pack, string


    def test_stringatom_unpack():
        # The string atom works as a basic converter between
        # bytes and unicode objects.
        assert unpack(b"foo", string(3, "utf-8")) == "foo"


