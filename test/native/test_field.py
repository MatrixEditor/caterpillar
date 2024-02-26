# pylint: disable=import-error,no-name-in-module
from caterpillar._core import CpField, CpOption, CpEndian, CpArch, CpAtom, CpFieldAtom

import pytest

A = CpAtom()


def test_field_init():
    f = CpField(CpAtom())
    assert f.atom

    with pytest.raises(TypeError):
        f = CpField()

    f = CpField(A, offset=0xF00)
    assert f.offset == 0xF00


def test_field_length():
    f = CpField(A, length=0xF00)
    assert f.length == 0xF00

    f = CpField(A)[10]
    assert f.length == 10

    f = CpField(A)[...]
    assert f.length is ...

    f = CpField(A)[A::]
    assert isinstance(f.length, slice)

    with pytest.raises(TypeError):
        f = CpField(A)["foo"]


def test_field_offset():
    f = CpField(A, offset=0xF00)
    assert f.offset == 0xF00

    with pytest.raises(TypeError):
        f = CpField(A, offset="foo")

    f = CpField(A) @ 10
    assert f.offset == 10

    f = CpField(A) @ (lambda x: 1)
    assert callable(f.offset)


def test_field_conditionn():
    f = CpField(A) // False
    assert f.condition is False

    f = CpField(A) // (lambda x: False)
    assert callable(f.condition)
