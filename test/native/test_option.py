# pylint: disable=import-error,no-name-in-module
from caterpillar._core import CpOption

import pytest


def test_option_init():
    o = CpOption(name="foo")

    assert o.value is None
    assert o.name == "foo"

    with pytest.raises(ValueError):
        o = CpOption()

    with pytest.raises(TypeError):
        o = CpOption(name=0xF00, value="bar")


def test_option_cmp():
    foo = CpOption(name="foo")
    bar = CpOption(name="bar")

    assert foo != bar
    assert foo == CpOption(name="foo")
    assert foo > bar

    assert foo in {foo}
