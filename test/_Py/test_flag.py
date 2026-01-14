from caterpillar.options import (
    Flag,
    configure,
    GLOBAL_STRUCT_OPTIONS,
    get_flag,
    get_flags,
)
from caterpillar.py import Context


def test_flag_value():
    # Each flag stores a value which can be used
    # to configure fields and structs.
    flag: Flag[int] = Flag("test1", None)
    assert flag.value is None

    flag.value = 1
    assert flag.value == 1


def test_flag_hash():
    # Flags/Options can be stored in a set to keep track of
    # unique options
    options: set[Flag] = set()
    options.add(Flag("a"))

    # of course, length is now 1
    assert len(options) == 1

    # checking whether a flag is stored inside the set must
    # work
    assert Flag("b") not in options
    assert Flag("a") in options


def test_flag_compare():
    # Comparison between two _OptionLike objects should be done
    # based on the .name attribute
    flag_a = Flag("a")
    flag_b = Flag("b")
    assert flag_a != flag_b

    # check should succeed now
    flag_b.name = "a"
    assert flag_a == flag_b


def test_flag_globals():
    # options can be enabled globally. They may affect the behaviour
    # of certain structs, packing or unpacking.
    flag_a = Flag("a")
    flag_b = Flag("b")
    configure(GLOBAL_STRUCT_OPTIONS, flag_a, flag_b)

    # both options are now enabled globally
    assert flag_a in GLOBAL_STRUCT_OPTIONS and flag_b in GLOBAL_STRUCT_OPTIONS
    GLOBAL_STRUCT_OPTIONS.remove(flag_a)
    GLOBAL_STRUCT_OPTIONS.remove(flag_b)
    assert flag_a not in GLOBAL_STRUCT_OPTIONS


def test_has_flag():
    # if an object stores its flags in .flags, the global method
    # has_flag can be used to determine whether a specific option
    # has been set.
    flag_a = Flag("a")
    obj = Context(flags=set())

    flags = get_flags(obj)
    assert len(flags) == 0  # should be empty

    obj.flags.add(flag_a)  # pyright: ignore[reportAny]
    assert flag_a in get_flags(obj)
    assert get_flag("a", obj) is not None
