import pytest

from caterpillar.py import (
    DynamicSizeError,
    Memory,
    pack,
    root,
    sizeof,
    unpack,
    ValidationError,
)


def test_py_memory_unpack():
    memory = Memory(10)
    assert unpack(memory, b"1234567890") == b"1234567890"


def test_py_memory_pack():
    memory = Memory(10)
    assert pack(b"1234567890", memory) == b"1234567890"


def test_py_memory_length_int():
    value = b"A" * 10
    field = Memory(10)

    assert sizeof(field) == 10
    assert pack(value, field) == value

    # invalid input object will raise an exception
    with pytest.raises(ValidationError):
        _ = pack(b"A" * 11, field)


def test_py_memory_length_dyn():
    length = 10
    value = b"A" * length
    # Length can be a context path that points to the field that
    # stores the length
    field = Memory(root.length)

    # The length must be set otherwise there will be an error
    assert sizeof(field, length=length) == length
    with pytest.raises(AttributeError):
        _ = sizeof(field)

    assert pack(value, field, length=length) == value
    with pytest.raises(ValidationError):
        _ = pack(value[1:], field, length=length)


def test_py_memory_length_greedy():
    field = Memory(...)
    value = b"A" * 256
    with pytest.raises(DynamicSizeError):
        # greedy length is dynamic
        assert sizeof(field)

    assert pack(value, field) == value
    assert unpack(field, value) == value
