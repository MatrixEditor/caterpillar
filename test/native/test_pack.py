# pylint: disable=import-error,no-name-in-module
from caterpillar._core import (
    CpField,
    CpOption,
    CpEndian,
    CpArch,
    CpAtom,
    CpFieldAtom,
    pack_into,
    CpState,
    pack,
    CpLayer,
)
from io import BytesIO

import pytest


class Foo(CpFieldAtom):
    def __pack__(self, obj, layer: CpLayer):
        layer.state.write(obj.to_bytes(1, "big"))


foo_t = Foo()


@pytest.mark.parametrize(
    ("f", "data", "target"),
    [
        (foo_t, 1, b"\x01"),
        (foo_t[2], [1] * 2, b"\x01\x01"),
        (foo_t[...], [1] * 10, b"\x01" * 10),
        (foo_t[foo_t::], [1] * 2, b"\x02\x01\x01"),
    ],
)
def test_pack_into(f, data, target):
    with BytesIO() as stream:
        pack_into(data, f, stream)
        assert stream.getvalue() == target
