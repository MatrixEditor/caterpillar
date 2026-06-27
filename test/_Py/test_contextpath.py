from types import SimpleNamespace

import pytest

from caterpillar.py import Context, ctx as context_path, f, parent, pack, root, struct, this, uint8, unpack


def sample_context():
    obj = SimpleNamespace(
        a=5,
        b=SimpleNamespace(c=7),
        items=[10, 20],
        mapping={"x": 9},
    )
    return Context(
        _obj=obj,
        _parent=Context(_obj=SimpleNamespace(a=99)),
        _root=Context(root_value=123),
    )


def test_simple_nested_parent_root():
    context = sample_context()

    assert this(context) is context["_obj"]
    assert this.a(context) == 5
    assert this.b.c(context) == 7
    assert parent.a(context) == 99
    assert root.root_value(context) == 123
    assert context_path(context) is context


def test_indexing_and_mapping_lookup():
    context = sample_context()

    assert this.items[0](context) == 10
    assert this.items[1](context) == 20
    assert this.mapping["x"](context) == 9


def test_arithmetic_bitwise_and_comparison_expressions():
    context = sample_context()

    assert (this.a + 2)(context) == 7
    assert (2 + this.a)(context) == 7
    assert (this.b.c - this.a)(context) == 2
    assert (this.a * this.b.c)(context) == 35
    assert (this.b.c / 2)(context) == 3.5
    assert (this.b.c // 2)(context) == 3
    assert (this.b.c % 5)(context) == 2
    assert (this.a & 3)(context) == 1
    assert (this.a | 2)(context) == 7
    assert (this.a ^ 7)(context) == 2
    assert (this.a == 5)(context) is True
    assert (this.a != 5)(context) is False
    assert (this.a < this.b.c)(context) is True
    assert (this.b.c >= this.a)(context) is True
    assert (~this.a)(context) == ~5


def test_missing_path_index_and_mapping_key():
    context = sample_context()

    with pytest.raises(AttributeError):
        this.nope(context)
    with pytest.raises(IndexError):
        this.items[9](context)
    with pytest.raises(KeyError):
        this.mapping["z"](context)


def test_context_path_length():
    @struct
    class Packet:
        n: f[int, uint8]
        data: f[list[int], uint8[this.n]]

    decoded = unpack(Packet, b"\x03abc")

    assert decoded.n == 3
    assert decoded.data == [97, 98, 99]
    assert pack(Packet(n=2, data=[65, 66]), Packet) == b"\x02AB"


def test_indexing_context_path_is_immutable():
    context = sample_context()
    base = this.items

    first = base[0]
    second = base[1]

    assert first(context) == 10
    assert second(context) == 20
