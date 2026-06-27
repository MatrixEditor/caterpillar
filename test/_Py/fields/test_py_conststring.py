import pytest

from caterpillar.py import ConstString, ValidationError, pack, unpack


def test_ascii_pack_ignores_input_and_writes_constant():
    field = ConstString("OK")
    assert pack(None, field) == b"OK"
    # the type checker should scream at you here
    assert pack("wrong", field) == b"OK"


def test_ascii_unpack_requires_exact_constant():
    field = ConstString("OK")
    assert unpack(field, b"OK") == "OK"


def test_empty_constant_roundtrip():
    field = ConstString("")
    assert pack(None, field) == b""
    assert unpack(field, b"") == ""


def test_unpack_mismatch_raises():
    with pytest.raises(ValidationError):
        _ = unpack(ConstString("OK"), b"NO")


def test_constructor_rejects_non_string_value():
    with pytest.raises(TypeError):
        _ = ConstString(b"not a str")


def test_multibyte_constant_packs_encoded_bytes():
    field = ConstString("é", encoding="utf-8")
    assert pack(None, field) == "é".encode("utf-8")


def test_multibyte_constant_unpacks_encoded_bytes():
    field = ConstString("é", encoding="utf-8")
    assert unpack(field, "é".encode("utf-8")) == "é"


def test_multibyte_constant_bits_use_encoded_byte_count():
    field = ConstString("é", encoding="utf-8")
    assert field.__bits__ == len("é".encode("utf-8")) * 8


def test_array_of_const_strings():
    seq = ConstString("X")[3]
    # even though this is possible, the type checker should warn you
    # about the pack() call. It expects all elements to be None.
    assert pack([None, "ignored", object()], seq) == b"XXX"
    assert unpack(seq, b"XXX") == ["X", "X", "X"]
