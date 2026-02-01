from caterpillar.py import Prefixed, pack, unpack, uint8, Bytes, uint16

def test_prefixed_bytes():
    atom = Prefixed(uint8)
    assert pack(b"foo", atom) == b"\x03foo"
    assert unpack(atom, b"\x03foo") == b"foo"


def test_prefixed_encoding():
    # fmt: off
    atom = Prefixed(uint8, encoding="utf-8")

    assert unpack(atom, b"\x03foo") == "foo"
    # the following line is expected to raise errors to static type checkers, since
    # they don't know the Prefixed type applies the utf-8 encoding.
    assert pack("foo", atom) == b"\x03foo"  # pyright: ignore[reportCallIssue, reportArgumentType]


def test_prefixed_bytes_struct():
    atom = Prefixed(uint8, Bytes(...))
    assert unpack(atom, b"\x03foo") == b"foo"
    assert pack(b"foo", atom) == b"\x03foo"


def test_prefixed_custom_struct():
    atom = Prefixed(uint8, uint16[...])
    assert unpack(atom, b"\x04\x01\x00\x01\x00") == [1, 1]
    assert pack([1, 1], atom) == b"\x04\x01\x00\x01\x00"
