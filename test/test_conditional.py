# file: test_conditional
# All tests performed in this file are related to conditional fields in
# a class definition. They are not just tests, but can be used as examples
# too.
import pytest

from caterpillar.fields import uint8, uint32, uint16, If, Else, ElseIf
from caterpillar.shortcuts import struct, BigEndian, this
from struct import error

from _utils import _test_pack, _test_unpack


###############################################################################
# inline condition
###############################################################################
@struct
class Format_InlineCondition:
    a: uint8
    with this.a == 10:
        b: uint8


def test_inline_condition_init():
    obj = Format_InlineCondition(1)
    assert obj.b is None, "Field 'b' should be None"


def test_inline_condition_pack():
    _test_pack(Format_InlineCondition(10, b=0xFF), b"\x0A\xFF")


def test_inline_condition_unpack():
    _test_unpack(Format_InlineCondition, b"\x0B\xFF", Format_InlineCondition(0xB))
    _test_unpack(
        Format_InlineCondition, b"\x0A\xFF", Format_InlineCondition(0xA, b=0xFF)
    )


###############################################################################
# inline condition within inline condition
###############################################################################
@struct
class Format_InlineInlineCondition:
    a: uint8
    with this.a == 10:
        b: uint8
        with this.b == 10:
            c: uint8


def test_inline_inline_condition_pack():
    _test_pack(Format_InlineInlineCondition(10, b=0xFF), b"\x0A\xFF")
    _test_pack(Format_InlineInlineCondition(10, b=10, c=0xFF), b"\x0A\x0A\xFF")


def test_inline_inline_condition_unpack():
    _test_unpack(
        Format_InlineInlineCondition, b"\x0B", Format_InlineInlineCondition(0xB)
    )
    _test_unpack(
        Format_InlineInlineCondition,
        b"\x0A\xFF",
        Format_InlineInlineCondition(0xA, b=0xFF),
    )
    _test_unpack(
        Format_InlineInlineCondition,
        b"\x0A\x0A\xFF",
        Format_InlineInlineCondition(0xA, b=0xA, c=0xFF),
    )


###############################################################################
# simple IF-statement
###############################################################################
@struct
class Format_If:
    a: uint8
    with If(this.a > 9):
        b: uint8


def test_if_condition_pack():
    _test_pack(Format_If(10, b=0xFF), b"\x0A\xFF")
    _test_pack(Format_If(9), b"\x09")


def test_if_unpack():
    _test_unpack(Format_If, b"\x09", Format_If(9))
    _test_unpack(Format_If, b"\x0A\xFF", Format_If(0xA, b=0xFF))


###############################################################################
# simple IF-ELSE statement
###############################################################################
@struct(order=BigEndian)
class Format_IfElse:
    a: uint8
    with If(this.a > 9):
        b: uint8
    with Else:
        b: uint16


def test_ifelse_condition_pack():
    _test_pack(Format_IfElse(10, b=0xFF), b"\x0A\xFF")
    _test_pack(Format_IfElse(9, b=0xFF), b"\x09\x00\xFF")


def test_ifelse_condition_unpack():
    _test_unpack(Format_IfElse, b"\x09\x00\xFF", Format_IfElse(9, b=0xFF))
    _test_unpack(Format_IfElse, b"\x0A\xFF", Format_IfElse(10, b=0xFF))


###############################################################################
# simple IF-ELSEIF-ELSE statement
###############################################################################
@struct(order=BigEndian)
class Format_IfElseIfElse:
    a: uint8
    with If(this.a <= 9):
        b: uint8
    with ElseIf(this.a < 16):
        b: uint16
    with Else:
        b: uint32


def test_if_elseif_else_condition_pack():
    _test_pack(Format_IfElseIfElse(9, b=0xFF), b"\x09\xFF")
    _test_pack(Format_IfElseIfElse(10, b=0xFF), b"\x0A\x00\xFF")
    _test_pack(Format_IfElseIfElse(16, b=0xFF), b"\x10\x00\x00\x00\xFF")


###############################################################################
# complex conditional branches
###############################################################################
@struct(order=BigEndian)
class Format_ComplexConditional:
    a: uint8
    with this.a == 10:
        b: uint16
        with If(this.b > 10):
            c: uint8
            d: uint8
        # we can't use 'Else' here
        with ElseIf(this.b <= 10):
            d: uint32


def test_complex_condition_pack():
    _test_pack(
        Format_ComplexConditional(10, b=11, c=0xFF, d=0xFF), b"\x0A\x00\x0B\xFF\xFF"
    )
    with pytest.raises(error):
        _test_pack(Format_ComplexConditional(10, b=11, d=0xFFFF), b"\x0A\x00\x0B")
    _test_pack(Format_ComplexConditional(10, b=11, d=0xFF), b"\x0A\x00\x0B\xFF")
    _test_pack(
        Format_ComplexConditional(10, b=10, d=0xFFFF), b"\x0A\x00\x0A\x00\x00\xFF\xFF"
    )
