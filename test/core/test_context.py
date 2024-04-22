# pylint: disable=unused-import, no-name-in-module
import pytest

from caterpillar._core import Context, ContextPath


def test_context_init():
    """Simple tests around the Context class."""
    c1 = Context()
    assert len(c1) == 0

    c1.foo = 1
    assert len(c1) == 1

    c2 = Context(foo=1, bar=2)
    assert len(c2) == 2
    assert c2.foo == 1 and c2.bar == 2


def test_context_getattr():
    """Simple tests around the Context class using getattr"""
    c = Context(foo=1, bar=2)

    assert getattr(c, "foo") == 1
    assert getattr(c, "bar") == 2
    # This call will be transferred to the __context_getattr__ function
    assert getattr(c, "foo.__class__") == int

    with pytest.raises(AttributeError):
        # this class is strict when it comes to undefined
        # members
        _ = c.baz


def test_contextpath():
    """Simple tests around the ContextPath class."""
    c = Context(foo=1, bar=2)
    cp = ContextPath("foo")
    assert cp(c) == 1
    cp = ContextPath("bar.__class__")
    assert cp(c) == int
    # Special attributes must be defined within the
    # constructor call
    assert cp.__class__ == ContextPath

    with pytest.raises(AttributeError):
        ContextPath("baz")(cp)


@pytest.mark.parametrize(
    "name, func, expected",
    [
        ("__add__", lambda x: x + 3, 4),
        ("__sub__", lambda x: x - 3, -2),
        ("__mul__", lambda x: x * 3, 3),
        ("__floordiv__", lambda x: x // 3, 0),
        ("__truediv__", lambda x: x / 3, 1 / 3),
        ("__mod__", lambda x: x % 3, 1),
        ("__pow__", lambda x: x ** 3, 1),
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
def test_ops(name, func, expected):
    # Context value starts at one
    cp = Context(foo=1)
    # path always points too foo
    path = func(ContextPath("foo"))
    rval = path(cp)
    assert rval == expected, f"Invalid result: {rval} - expected {expected} on {name}"
