import pytest
import typing

# pylint: disable-next=import-error,wildcard-import,no-name-in-module
from caterpillar._core import CpAtom, CpStruct, S_REPLACE_TYPES


class Format:
    foo: CpAtom()


def test_struct_init():
    s = CpStruct(Format)

    assert s.model is Format
    assert len(s.members) == 1
    assert "foo" in s.members

    with pytest.raises(ValueError):
        # field 'foo' is required
        f = Format()

    assert Format(1).foo == Format(foo=1).foo


def test_struct_default_init():
    class A:
        foo: CpAtom() = None

    s = CpStruct(A)
    assert len(s.members) == 1
    assert s.members["foo"].field.default is None

    a = A()
    b = A(foo=1)
    # keyword arg has higher priority than default value
    assert a.foo != b.foo

def test_struct_replace_types():
    s = CpStruct(Format, options={S_REPLACE_TYPES})
    assert s.model is Format
    assert len(s.members) == 1
    assert "foo" in s.members
    assert Format.__annotations__["foo"] == typing.Any