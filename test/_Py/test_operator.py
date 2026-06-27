from types import SimpleNamespace

import pytest

from caterpillar.py import Context, Operator, pack, this, uint8, unpack


def test_operator_infix_builds_sequence_field():
    Repeat = Operator(lambda struct, count: struct[count])

    field = uint8 / Repeat / 3

    assert pack([1, 2, 3], field) == b"\x01\x02\x03"
    assert unpack(field, b"\x01\x02\x03") == [1, 2, 3]


def test_operator_can_be_used_as_decorator_and_direct_call():
    @Operator
    def TimesTwo(struct, count):
        return struct[count * 2]

    field = uint8 / TimesTwo / 2
    direct = TimesTwo(uint8, 1)

    assert pack([1, 2, 3, 4], field) == b"\x01\x02\x03\x04"
    assert unpack(field, b"\x01\x02\x03\x04") == [1, 2, 3, 4]
    assert pack([9, 10], direct) == b"\x09\x0a"


def test_operator_partial_stage_waits_for_right_operand():
    Repeat = Operator(lambda struct, count: struct[count])

    stage = uint8 / Repeat
    field = stage / 2

    assert isinstance(stage, Operator)
    assert pack([8, 9], field) == b"\x08\x09"


def test_context_expression_operators_and_precedence():
    context = Context(_obj=SimpleNamespace(a=10, b=3, mask=0b1010))

    assert (this.a + this.b)(context) == 13
    assert (this.a - this.b)(context) == 7
    assert (this.a * this.b)(context) == 30
    assert (this.a / this.b)(context) == pytest.approx(10 / 3)
    assert (this.a // this.b)(context) == 3
    assert (this.a % this.b)(context) == 1
    assert (this.b**2)(context) == 9
    assert (this.mask & 0b0110)(context) == 0b0010
    assert (this.mask | 0b0101)(context) == 0b1111
    assert (this.mask ^ 0b1111)(context) == 0b0101
    assert (this.a << 1)(context) == 20
    assert (this.a >> 1)(context) == 5
    assert (this.a == 10)(context) is True
    assert (this.a != 10)(context) is False
    assert (this.a > this.b)(context) is True
    assert (this.b <= this.a)(context) is True
    assert (this.a + this.b * 2)(context) == 16
    assert ((this.a + this.b) * 2)(context) == 26


def test_unary_invert_uses_python_bitwise_semantics():
    context = Context(_obj=SimpleNamespace(mask=0b1010))

    assert (~this.mask)(context) == ~0b1010
