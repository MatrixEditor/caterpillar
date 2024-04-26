# pylint: disable=no-name-in-module,unused-import
import pytest

from caterpillar._C import Option
from caterpillar._C import (
    F_DYNAMIC,
    F_SEQUENTIAL,
    S_DISCARD_UNNAMED,
    S_REPLACE_TYPES,
    S_SLOTS,
    S_UNION,
    S_EVAL_ANNOTATIONS,
)
from caterpillar._C import FIELD_OPTIONS, STRUCT_OPTIONS


@pytest.mark.parametrize(
    "option",
    [
        S_DISCARD_UNNAMED,
        S_REPLACE_TYPES,
        S_SLOTS,
        S_UNION,
        S_EVAL_ANNOTATIONS,
    ],
)
def test_option(option: Option):
    """Simply cosistency check."""
    assert option.name.startswith("struct:")

    STRUCT_OPTIONS.add(option)
    assert option in STRUCT_OPTIONS


@pytest.mark.parametrize(
    "option",
    [
        F_DYNAMIC,
        F_SEQUENTIAL,
    ],
)
def test_field_option(option: Option):
    """Simply cosistency check."""
    assert option.name.startswith("field:")

    FIELD_OPTIONS.add(option)
    assert option in FIELD_OPTIONS
