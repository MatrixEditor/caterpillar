import pytest
import typing

# pylint: disable-next=import-error,wildcard-import,no-name-in-module
from caterpillar._core import CpAtom, CpStruct, S_REPLACE_TYPES, pack, CpField


class Format:
    foo: CpAtom()


def test_struct_init():
    S = CpStruct(Format, alter_model=True)

    assert S.model is Format
    assert len(S.members) == 1
    assert "foo" in S.members

    with pytest.raises(ValueError):
        # field 'foo' is required
        f = Format()

    assert Format(1).foo == Format(foo=1).foo


def test_struct_default_init():
    class A:
        foo: CpAtom() = None

    s = CpStruct(A, alter_model=True)
    assert len(s.members) == 1
    assert s.members["foo"].field.default is None

    a = A()
    b = A(foo=1)
    # keyword arg has higher priority than default value
    assert a.foo != b.foo


def test_struct_replace_types():
    class Format2:
        foo: CpAtom()

    s = CpStruct(Format2, options={S_REPLACE_TYPES}, alter_model=True)
    assert s.model is Format2
    assert len(s.members) == 1
    assert "foo" in s.members
    assert Format2.__annotations__["foo"] == typing.Any


class IntAtom(CpAtom):
    def __pack__(self, obj, context):
        context.write(obj.to_bytes(2))

    def __type__(self):
        return int


def test_struct_pack():

    class IntFormat:
        foo: IntAtom()

    C = CpStruct(IntFormat, options={S_REPLACE_TYPES}, alter_model=True)

    s = C
    assert len(s.members) == 1
    assert IntFormat.__annotations__["foo"] == int

    assert pack(IntFormat(2), s) == b"\x00\x02"

    assert pack(IntFormat(foo=2), s) == b"\x00\x02"


def test_struct_pack_seq():
    class IntFormat2:
        foo: IntAtom()

    f = CpField(CpStruct(IntFormat2, alter_model=True))[2]
    assert f.length == 2

    result = pack([IntFormat2(1), IntFormat2(2)], f)
    assert result == b"\x00\x01\x00\x02"
