import pytest

from caterpillar.py import InvalidValueError, pack, root, unpack
from caterpillar.fields.crypto import KeyCipher


class ToyXor(KeyCipher):
    def _do_process(self, src: bytes, dest: bytearray) -> None:
        for index, value in enumerate(src):
            dest[index] = value ^ self.key[index % self.key_length]


def test_key_accepts_bytes_string_and_single_byte_int():
    assert ToyXor(b"A", 1).key == b"A"
    assert ToyXor("A", 1).key == b"A"
    assert ToyXor(0x41, 1).key == b"A"


def test_non_key_types_are_rejected():
    with pytest.raises(InvalidValueError):
        ToyXor(bytearray(b"A"), 1)

    with pytest.raises(InvalidValueError):
        ToyXor(None, 1)


def test_process_is_used_for_pack_and_unpack():
    field = ToyXor(b"\x01\x02", 4)
    ciphertext = pack(b"abcd", field)

    assert ciphertext == b"``bf"
    assert unpack(field, ciphertext) == b"abcd"


def test_key_shorter_than_payload_repeats_from_base_class_state():
    field = ToyXor(b"\x01\x02", 5)

    assert pack(b"\x00\x00\x00\x00\x00", field) == b"\x01\x02\x01\x02\x01"


def test_lazy_key_works_for_first_context():
    field = ToyXor(root.key, 3)

    assert pack(b"abc", field, key=b"\x01") == b"`cb"
    assert unpack(field, b"`cb", key=b"\x01") == b"abc"


def test_lazy_key_is_recomputed_for_each_operation_context():
    field = ToyXor(root.key, 3)

    assert pack(b"abc", field, key=b"\x01") == b"`cb"
    assert pack(b"abc", field, key=b"\x02") == b"c`a"
