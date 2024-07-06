# pylint: disable=unused-import,no-name-in-module,import-error
import pytest

from caterpillar._C import unpack, pack, padding, paddingatom


def test_padding_pack():
    # The padding atom is special, because it does not need
    # an input value and its error policy is very lax.
    assert pack(None, padding) == b"\x00"

    # In addition, we can define custom padding values,
    # which will affect only packing data.
    assert pack(None, paddingatom(0x20)) == b"\x20"

def test_padding_pack_many():
    # The padding atom also implements __pack_many__ and
    # __unpack_many__. (Time measurements are work in progress).
    assert pack(None, padding[10]) == b"\x00" * 10
    assert pack(None, paddingatom(0x20)[10]) == b"\x20" * 10

    # REVISIT: this should return an exception
    # with pytest.raises(ValueError):
    #     pack(None, padding[...])

def test_padding_unpack():
    # NOTE: unpack using the padding atom always returns None
    # and DOES NOT validate the parsed value.
    assert unpack(b"\x00", padding) is None
    assert unpack(b"\x20", paddingatom(0x20)) is None

    # Therefore, the following code IS valid if the underlying
    # stream does not throw an exception.
    assert unpack(b"\x00", padding[10]) is None

def test_padding_unpack_many():
    assert unpack(b"\x00" * 10, padding[10]) is None
    assert unpack(b"\x20" * 10, paddingatom(0x20)[10]) is None