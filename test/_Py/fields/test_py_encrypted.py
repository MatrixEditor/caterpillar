from io import BytesIO

import pytest

pytest.importorskip("cryptography")

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from caterpillar.py import ValidationError, pack, root, unpack
from caterpillar.fields.crypto import Encrypted


AES_KEY = b"\x00" * 16
AES_WRONG_KEY = b"\xff" * 16
AES_IV = b"\x01" * 16


def _aes_cbc(length, pad=None, key=AES_KEY):
    return Encrypted(length, algorithms.AES, modes.CBC, pad, [key], [AES_IV])


def _aes_ctr(length, key=AES_KEY):
    return Encrypted(length, algorithms.AES, modes.CTR, None, [key], [AES_IV])


def test_aes_cbc_without_padding_for_exact_block():
    field = _aes_cbc(16)
    plaintext = b"0123456789abcdef"

    ciphertext = pack(plaintext, field)

    assert ciphertext != plaintext
    assert len(ciphertext) == 16
    assert bytes(unpack(field, ciphertext)) == plaintext


def test_aes_cbc_pkcs7_padding_for_short_plaintext():
    field = _aes_cbc(16, padding.PKCS7(128))
    plaintext = b"hi"

    ciphertext = pack(plaintext, field)

    assert len(ciphertext) == 16
    assert bytes(unpack(field, ciphertext)) == plaintext


def test_wrong_key_fails_cleanly_with_authenticated_padding_check():
    good = _aes_cbc(16, padding.PKCS7(128))
    wrong = _aes_cbc(16, padding.PKCS7(128), key=AES_WRONG_KEY)
    ciphertext = pack(b"attack at dawn", good)

    with pytest.raises(ValueError, match="padding"):
        unpack(wrong, ciphertext)


def test_block_cipher_without_padding_rejects_non_block_plaintext():
    with pytest.raises(ValueError, match="block length"):
        pack(b"short", _aes_cbc(16))


def test_fixed_length_is_ciphertext_length_and_stream_consumption():
    field = _aes_ctr(4)
    ciphertext = pack(b"DATA", field)
    stream = BytesIO(ciphertext + b"tail")

    assert len(ciphertext) == 4
    assert bytes(unpack(field, stream)) == b"DATA"
    assert stream.tell() == 4


def test_fixed_length_rejects_ciphertext_size_mismatch():
    with pytest.raises(ValidationError, match="expected 4 bytes"):
        pack(b"abc", _aes_ctr(4))


def test_context_lambdas_can_supply_algorithm_and_mode_args():
    field = Encrypted(
        4,
        algorithms.AES,
        modes.CTR,
        None,
        [root.key],
        [root.iv],
    )

    ciphertext = pack(b"ABCD", field, key=AES_KEY, iv=AES_IV)

    assert ciphertext != b"ABCD"
    assert bytes(unpack(field, ciphertext, key=AES_KEY, iv=AES_IV)) == b"ABCD"


def test_padding_class_and_args_are_instantiated_before_use():
    field = Encrypted(
        16,
        algorithms.AES,
        modes.CBC,
        padding.PKCS7,
        [AES_KEY],
        [AES_IV],
        [128],
    )

    ciphertext = pack(b"hi", field)

    assert bytes(unpack(field, ciphertext)) == b"hi"
