import pytest

from caterpillar.py import Else, If, f, pack, struct, this, uint8, uint16, unpack


def define_optional_byte():
    @struct
    class OptionalByte:
        flag: f[int, uint8]
        with If(this.flag == 1):
            value: f[int, uint8]
        trailer: f[int, uint8]

    return OptionalByte


@pytest.mark.xfail(
    reason="If cannot access class __annotations__ on Python 3.14;"
)
def test_if_unpacks_true_branch():
    OptionalByte = define_optional_byte()

    decoded = unpack(OptionalByte, b"\x01\xaa\xff")

    assert decoded.flag == 1
    assert decoded.value == 0xAA
    assert decoded.trailer == 0xFF


@pytest.mark.xfail(
    reason="If cannot access class __annotations__ on Python 3.14;"
)
def test_if_false_branch_consumes_no_bytes_and_returns_default_none():
    OptionalByte = define_optional_byte()

    decoded = unpack(OptionalByte, b"\x00\xff")

    assert decoded.flag == 0
    assert decoded.value is None
    assert decoded.trailer == 0xFF


@pytest.mark.xfail(
    reason="If cannot access class __annotations__ on Python 3.14;"
)
def test_if_pack_false_branch_writes_nothing_for_disabled_field():
    OptionalByte = define_optional_byte()

    assert pack(OptionalByte(flag=0, value=0xAA, trailer=0xFF), OptionalByte) == b"\x00\xff"
    assert pack(OptionalByte(flag=1, value=0xAA, trailer=0xFF), OptionalByte) == b"\x01\xaa\xff"


