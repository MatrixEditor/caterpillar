# pylint: disable=unused-import,no-name-in-module,import-error
import pytest
import caterpillar

if caterpillar.native_support():

    from caterpillar._C import State, layer, ContextPath, Context


    # State and layer each implement the context protocol, we
    # should verify that they are working as expected.
    def test_state_init():
        """Simple tests around the State class."""
        s1 = State()
        assert len(s1.globals) == 0

        s1.globals.foo = 1
        assert s1.globals.foo == 1
        assert s1.io is None
        assert len(s1.offset_table) == 0


    def test_layer_init():
        """Simple tests around the layer class."""
        with pytest.raises(TypeError):
            _ = layer()

        l = layer(State())
        assert l.obj is None
        l.obj = 1
        assert l.obj == 1


    @pytest.mark.parametrize(
        "name, func, expected",
        [
            ("__add__", lambda x: x + 3, 4),
            ("__sub__", lambda x: x - 3, -2),
            ("__mul__", lambda x: x * 3, 3),
            ("__floordiv__", lambda x: x // 3, 0),
            ("__truediv__", lambda x: x / 3, 1 / 3),
            ("__mod__", lambda x: x % 3, 1),
            ("__pow__", lambda x: x**3, 1),
            ("__lshift__", lambda x: x << 3, 8),
            ("__rshift__", lambda x: x >> 3, 0),
            ("__and__", lambda x: x & 3, 1),
            ("__or__", lambda x: x | 3, 3),
            ("__xor__", lambda x: x ^ 3, 2),
            ("__neg__", lambda x: -x, -1),
            ("__pos__", lambda x: +x, 1),
            ("__invert__", lambda x: ~x, -2),
        ],
    )
    def test_context_path_ops(name, func, expected):
        # Context value starts at one
        c = Context(foo=1)
        cp2 = ContextPath("obj.foo")
        # path always points to foo
        path2 = func(cp2)
        l = layer(State(), obj=c)
        rval = path2(l)
        assert (
            rval == expected
        ), f"Invalid result: {rval} - expected {expected} on {name}"
