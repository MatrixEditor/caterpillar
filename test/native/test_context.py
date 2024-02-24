import pytest
from caterpillar._core import CpContext, CpContextPath


def test_context_init():
    c = CpContext()
    assert len(c) == 0

    c = CpContext(foo=1)
    assert len(c) == 1
    assert type(c) == CpContext


def test_context_access():
    c = CpContext(foo=1, bar=2)
    assert c["foo"] == 1
    assert c.bar == 2
    assert c.__class__ == CpContext

    c.x = 20
    assert c.x == 20


def test_contextpath():
    p = CpContextPath("foo")
    assert p.path == "foo"

    c = CpContext(foo=10)
    assert p(c) == 10

    with pytest.raises(TypeError):
        p(10)

    with pytest.raises(ValueError):
        p(None)

    p2 = CpContextPath("foo.__class__")
    assert p2(c) == int
    assert p.__class__ == CpContextPath
