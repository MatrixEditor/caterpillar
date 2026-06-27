from io import BytesIO

import lzma
import zlib

import pytest

from caterpillar.py import Bytes, pack, unpack
from caterpillar.fields.compression import (
    Bz2Compressed,
    Compressed,
    LZMACompressed,
    ZLibCompressed,
)


@pytest.mark.parametrize("payload", [b"", b"hello hello hello", bytes(range(256))])
def test_compressed_zlib(payload: bytes):
    field = Compressed(zlib, Bytes(...))

    compressed = pack(payload, field)

    assert compressed != payload or payload == b""
    assert unpack(field, compressed) == payload


def test_helper_factories_select_expected_algorithms():
    payload = b"algorithm selection"
    cases = [
        (ZLibCompressed, b"x"),
        (Bz2Compressed, b"BZh"),
        (LZMACompressed, b"\xfd7zXZ"),
    ]

    for factory, magic in cases:
        field = factory(...)
        compressed = pack(payload, field)

        assert compressed.startswith(magic)
        assert unpack(field, compressed) == payload


def test_corrupted_compressed_input_raises():
    with pytest.raises(zlib.error):
        unpack(ZLibCompressed(...), b"not a zlib stream")

    with pytest.raises(OSError):
        unpack(Bz2Compressed(...), b"not a bz2 stream")

    with pytest.raises(lzma.LZMAError):
        unpack(LZMACompressed(...), b"not an lzma stream")


def test_fixed_length_reads_only_wrapped_compressed_bytes():
    payload = b"abc"
    compressed = pack(payload, ZLibCompressed(...))
    stream = BytesIO(compressed + b"tail")

    assert unpack(ZLibCompressed(len(compressed)), stream) == payload
    assert stream.tell() == len(compressed)


def test_compression_kwargs_are_passed_to_algorithm():
    payload = b"A" * 256
    store = ZLibCompressed(..., comp_kwargs={"level": 0})
    shrink = ZLibCompressed(..., comp_kwargs={"level": 9})

    stored = pack(payload, store)
    shrunk = pack(payload, shrink)

    assert len(stored) > len(shrunk)
    assert unpack(store, stored) == payload
    assert unpack(shrink, shrunk) == payload

