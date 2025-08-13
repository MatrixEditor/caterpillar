import pytest
import caterpillar


if caterpillar.native_support():
    from caterpillar._C import Repeated
    from caterpillar.py import uint8, pack, unpack, Bytes, sizeof, typeof

    def testc_repeated_init():
        atom = Repeated(uint8, 3)
        assert atom.atom is uint8
        assert atom.length == 3

    def testc_repeated_pack():
        raw_data = b"\x01\x02\x03"
        py_data = [1, 2, 3]

        # The Repeated atom implements the sequence packing and
        # unpacking without needing a Field instance. However, types
        # that are not field agnostic will throw an exception here.
        # Default integer types are designed to support both field-agnostic
        # and field-specific length.
        atom = Repeated(uint8, 3)
        assert pack(py_data, atom) == raw_data

        atom = Repeated(Bytes(2), 3)
        py_data = [b"ab", b"cd", b"ef"]
        raw_data = b"".join(py_data)
        # default struct-like objects should work without any problems
        assert pack(py_data, atom) == raw_data

        # Prefixed length is supported too
        atom = Repeated(uint8, slice(uint8, None, 2))
        py_data = [1, 2, 3]
        raw_data = b"\x03\x01\x02\x03"
        assert pack(py_data, atom) == raw_data

        # Context Lambda should work too
        atom = Repeated(uint8, lambda context: context._root.length)
        py_data = [1, 2, 3]
        raw_data = b"\x01\x02\x03"
        assert pack(py_data, atom, length=3) == raw_data

    def testc_repeated_unpack():
        py_data = [b"ab", b"cd", b"ef"]
        raw_data = b"".join(py_data)
        # The Repeated atom implements the sequence packing and
        # unpacking without needing a Field instance. However, types
        # that are not field agnostic, will throw an exception here.
        atom = Repeated(Bytes(2), 3)
        assert unpack(atom, raw_data) == py_data

        # To temporarily support non-field agnostic types, use the
        # as_field argument. NOTE: this MAY lead to unintended side
        # effects.
        atom = Repeated(Bytes(2), slice(uint8, None, 2))
        assert unpack(atom, b"\x03" + raw_data) == py_data

        # Context Lambda should work too
        atom = Repeated(Bytes(2), lambda context: context._root.length)
        assert unpack(atom, raw_data, length=3) == py_data

    def testc_repeated_size():
        atom = Repeated(Bytes(2), 3)
        assert sizeof(atom) == 6

        # Dynamic length will raise an exception
        atom = Repeated(Bytes(2), slice(uint8, None, 2))
        with pytest.raises(ValueError):
            assert sizeof(atom) == 6

    def testc_repeated_type():
        atom = Repeated(Bytes(2), 3)
        assert typeof(atom) == list[bytes]
