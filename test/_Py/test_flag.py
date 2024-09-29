
import pytest

from caterpillar.py import Flag

def test_flag_value():
    # Each flag stores a value which can be used
    # to configure fields and structs.
    flag = Flag("test1", None)
    assert flag.value is None

    flag.value = 1
    assert flag.value == 1
