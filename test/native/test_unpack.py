# pylint: disable=import-error,no-name-in-module
from caterpillar._core import (
    CpFieldAtom,
    pack_into,
    CpLayer,
    unpack
)
from io import BytesIO
import pytest


class Foo(CpFieldAtom):
    def __pack__(self, obj, layer: CpLayer):
        layer.state.write(obj.to_bytes(1, "big"))

    def __unpack__(self, layer: CpLayer):
        return layer.state.read(1)[0]


foo_t = Foo()


@pytest.mark.parametrize(
    ("f", "target", "data"),
    [
        (foo_t, 1, b"\x01"),
        (foo_t[2], [1] * 2, b"\x01\x01"),
        (foo_t[...], [1] * 10, b"\x01" * 10),
        (foo_t[foo_t::], [1] * 2, b"\x02\x01\x01"),
    ],
)
def test_unpack(f, target, data):
    with BytesIO(data) as stream:
        val = unpack(stream, f)
        assert val == target
