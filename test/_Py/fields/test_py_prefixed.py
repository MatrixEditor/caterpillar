from caterpillar.py import Prefixed, pack, unpack, uint8, Bytes, uint16


def test_prefixed_bytes():
    atom = Prefixed(uint8)

    assert pack(b"foo", atom, as_field=True) == b"\x03foo"
    assert unpack(atom, b"\x03foo", as_field=True) == b"foo"


def test_prefixed_encoding():
    atom = Prefixed(uint8, encoding="utf-8")

    assert unpack(atom, b"\x03foo", as_field=True) == "foo"
    assert pack("foo", atom, as_field=True) == b"\x03foo"


def test_prefixed_bytes_struct():
    atom = Prefixed(uint8, Bytes(...))

    assert unpack(atom, b"\x03foo", as_field=True) == b"foo"
    assert pack(b"foo", atom, as_field=True) == b"\x03foo"


def test_prefixed_custom_struct():
    atom = Prefixed(uint8, uint16[...])

    assert unpack(atom, b"\x04\x01\x00\x01\x00", as_field=True) == [1, 1]
    assert pack([1, 1], atom, as_field=True) == b"\x04\x01\x00\x01\x00"
