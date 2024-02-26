import pytest
from caterpillar._core import (
    CpContext,
    CpContextPath,
    CpBinaryExpr,
    CpUnaryExpr,
    CpState,
)


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

    with pytest.raises(AttributeError):
        p(10)

    with pytest.raises(ValueError):
        p(None)

    p2 = CpContextPath("foo.__class__")
    assert p2(c) == int
    assert p.__class__ == CpContextPath


@pytest.mark.parametrize(
    ("value", "func", "target", "repr_str"),
    [
        (10, lambda p: p + 10, 20, "+ (10)"),
        (10, lambda p: p - 10, 0, "- (10)"),
        (10, lambda p: p * 10, 100, "* (10)"),
        (10, lambda p: p / 10, 1, "/ (10)"),
        (10, lambda p: p // 10, 1, "// (10)"),
        (10, lambda p: p % 10, 0, "% (10)"),
        (10, lambda p: p**10, 10000000000, "** (10)"),
        (1, lambda p: p << 10, 1024, "<< (10)"),
        (1024, lambda p: p >> 10, 1, ">> (10)"),
        (2, lambda p: p & 2, 2, "& (2)"),
        (128, lambda p: p | 2, 130, "| (2)"),
        (2, lambda p: p ^ 2, 0, "^ (2)"),
        (10, lambda p: p == 10, True, "== (10)"),
        (11, lambda p: p != 10, True, "!= (10)"),
        (12, lambda p: p < 10, False, "< (10)"),
        (1, lambda p: p > 10, False, "> (10)"),
        (9, lambda p: p <= 10, True, "<= (10)"),
        (11, lambda p: p >= 10, True, ">= (10)"),
    ],
)
def test_contextpath_binaryexpr(value, func, target, repr_str):
    p = CpContextPath("x")
    c = CpContext(x=value)

    expr = func(p)
    assert type(expr) == CpBinaryExpr
    assert repr(expr) == f"(CpPath('x')) {repr_str}"
    assert expr(c) == target


@pytest.mark.parametrize(
    ("value", "func", "target"),
    [
        (10, lambda p: -p, -10),
        (10, lambda p: ~p, -11),
        (-10, lambda p: +p, -10),
    ],
)
def test_contextpath_unaryexpr(value, func, target):
    p = CpContextPath("x")
    c = CpContext(x=value)

    expr = func(p)
    assert type(expr) == CpUnaryExpr
    assert expr(c) == target


def test_contextpath_state():
    s = CpState(io=1)
    p = CpContextPath("io.__class__")
    assert p(s) == int
