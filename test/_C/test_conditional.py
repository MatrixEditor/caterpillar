import pytest
import caterpillar

if caterpillar.native_support():
    from caterpillar._C import Conditional
    from caterpillar.py import ctx, pack, unpack, Bytes

    def testc_conditional_init():
        # simple declarative switch parsing
        atom = Conditional(
            Bytes(1),
            True,
        )
        assert atom.condition is True
