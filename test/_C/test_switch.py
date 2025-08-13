import pytest
import caterpillar
import enum

from caterpillar.shared import typeof


if caterpillar.native_support():
    from caterpillar._C import Switch
    from caterpillar.py import Bytes, String, ctx, pack, unpack
    from caterpillar.exception import ValidationError

    def testc_switch_init():
        # simple declarative switch parsing
        atom = Switch(
            Bytes(1),
            {
                b"a": String(1),
                b"b": String(2),
            },
        )
        assert atom.atom.length == 1
        assert len(atom.cases) == 2

    def testc_switch_pack():
        atom = Switch(
            ctx._root.target,
            {
                b"a": String(1),
                b"b": String(2),
            },
        )
        assert pack("a", atom, target=b"a") == b"a"
        assert pack("bb", atom, target=b"b") == b"bb"
        # will expect two bytes
        with pytest.raises(ValidationError):
            assert pack("c", atom, target=b"b")

    def testc_switch_unpack():
        class SomeType(enum.Enum):
            A = 1
            B = 2
            C = 3

        atom = Switch(
            ctx._root.target,
            {
                SomeType.A: String(1),
                SomeType.B: String(2),
            },
        )
        assert unpack(atom, b"a", target=SomeType.A) == "a"
        assert unpack(atom, b"bb", target=SomeType.B) == "bb"
        # will expect two bytes
        with pytest.raises(ValueError):
            assert unpack(atom, b"c", target=SomeType.C)

    def testc_switch_type():
        atom = Switch(
            ctx._root.target,
            {
                b"a": String(1),
                b"b": String(2),
            }
        )
        assert typeof(atom) == object | str