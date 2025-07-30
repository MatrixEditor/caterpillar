import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar._C import Conditional
    from caterpillar.py import ctx, pack, unpack, Bytes, sizeof

    def testc_conditional_init():
        # simple declarative switch parsing
        atom = Conditional(
            Bytes(1),
            True,
        )
        assert atom.condition is True

    def testc_conditional_type():
        # simple declarative switch parsing
        atom = Conditional(
            Bytes(1),
            True,
        )
        assert atom.__type__() == bytes | None

    def testc_conditional_size():
        # simple declarative switch parsing
        atom = Conditional(
            Bytes(1),
            True,
        )
        assert sizeof(atom) == 1

        atom = Conditional(
            Bytes(1),
            False,
        )
        assert sizeof(atom) == 0

    def testc_conditional_pack():
        # simple declarative switch parsing
        atom = Conditional(
            Bytes(1),
            True,
        )
        assert pack(b"a", atom) == b"a"

        atom = Conditional(
            Bytes(1),
            False,
        )
        assert pack(b"a", atom) == b""

    def testc_conditional_unpack():
        # simple declarative switch parsing
        atom = Conditional(
            Bytes(1),
            True,
        )
        assert unpack(atom, b"a") == b"a"

        atom = Conditional(
            Bytes(1),
            False,
        )
        assert unpack(atom, b"a") is None
