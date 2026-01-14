import pytest

from caterpillar.py import Memory, ctx, pack, unpack, ValidationError


def test_memory_unpack():
    memory = Memory(10)
    assert unpack(memory, b"1234567890", as_field=True) == b"1234567890"


def test_memory_pack():
    memory = Memory(10)
    assert pack(b"1234567890", memory, as_field=True) == b"1234567890"


def test_memory_length():
    memory = Memory(10)
    with pytest.raises(ValidationError):
        _ = pack(b"12345678901", memory, as_field=True)

    dyn_memory = Memory(lambda context: ctx._root.length(context))
    assert len(unpack(dyn_memory, b"123456789011", as_field=True, length=10)) == 10

    greedy_memory = Memory(...)
    assert len(unpack(greedy_memory, b"12345678901", as_field=True)) == 11
