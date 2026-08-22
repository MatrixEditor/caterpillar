# pyright: basic
import sys

import pytest

from caterpillar.py import (
    BigEndian,
    Branch,
    Else,
    ElseIf,
    End,
    If,
    Invisible,
    LittleEndian,
    Otherwise,
    Start,
    StructException,
    When,
    f,
    pack,
    struct,
    this,
    uint8,
    uint16,
    unpack,
)


# <3.14  SYNTAX:
def define_optional_byte():
    @struct
    class OptionalByte:
        flag: f[int, uint8]
        with If(this.flag == 1):
            value: f[int, uint8]
        trailer: f[int, uint8]

    return OptionalByte


# >=3.14 SYNTAX
def define_explicit_optional_byte():
    @struct
    class OptionalByte:
        flag: f[int, uint8]
        # With python3.14 it is required to assign the condition
        # manually or define block start end block end. The conditional
        # context allows direct [] (getitem) and indirect using Start/End (see below)
        with If(this.flag == 1) as when:
            value: when[f[int, uint8]]  # pyright: ignore[reportInvalidTypeForm]
        trailer: f[int, uint8]

    return OptionalByte


# >=3.14 SYNTAX
def define_marker_optional_byte():
    @struct
    class OptionalByte:
        flag: f[int, uint8]
        # Example with explicit block boundaries: We have to manually
        # define an attribute for the block's scope start and end. It
        # is recommended to use Invisible() on them to hide them from
        # the constructor.
        with If(this.flag == 1) as when:
            _: f[None, when] = Invisible()
            value: f[int, uint8]
            _end: f[None, End(when)] = Invisible()
        trailer: f[int, uint8]

    return OptionalByte


# >=3.14 SYNTAX
def define_inline_optional_byte():
    @struct
    class OptionalByte:
        flag: f[int, uint8]
        # markers and conditonal contexts can be applied as extra options
        # in the annotation too.
        with If(this.flag == 1) as when:
            value: f[int, uint8, when]
        trailer: f[int, uint8]

    return OptionalByte


@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Implicit 'with If(condition):' blocks are not supported on 3.14",
)
def test_if_unpacks_true_branch():
    OptionalByte = define_optional_byte()

    decoded = unpack(OptionalByte, b"\x01\xaa\xff")

    assert decoded.flag == 1
    assert decoded.value == 0xAA
    assert decoded.trailer == 0xFF


@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Implicit 'with If(condition):' blocks are not supported on 3.14",
)
def test_if_false_branch_consumes_no_bytes():
    OptionalByte = define_optional_byte()

    decoded = unpack(OptionalByte, b"\x00\xff")

    assert decoded.flag == 0
    assert decoded.value is None
    assert decoded.trailer == 0xFF


@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Implicit 'with If(condition):' blocks are not supported on 3.14",
)
def test_if_pack_false_branch_writes_nothing():
    OptionalByte = define_optional_byte()

    assert (
        pack(OptionalByte(flag=0, value=0xAA, trailer=0xFF), OptionalByte)
        == b"\x00\xff"
    )
    assert (
        pack(OptionalByte(flag=1, value=0xAA, trailer=0xFF), OptionalByte)
        == b"\x01\xaa\xff"
    )


def test_explicit_if_alias():
    OptionalByte = define_explicit_optional_byte()

    decoded = unpack(OptionalByte, b"\x01\xaa\xff")

    assert not hasattr(OptionalByte, "when")
    assert decoded.flag == 1
    assert decoded.value == 0xAA
    assert decoded.trailer == 0xFF


def test_explicit_if_alias_false_branch():
    OptionalByte = define_explicit_optional_byte()

    decoded = unpack(OptionalByte, b"\x00\xff")

    assert decoded.flag == 0
    assert decoded.value is None
    assert decoded.trailer == 0xFF
    assert pack(OptionalByte(flag=0, value=0xAA, trailer=0xFF)) == b"\x00\xff"


def test_explicit_if_alias_preserves_annotated_options():
    @struct(order=LittleEndian)
    class Packet:
        flag: f[int, uint8]
        with If(this.flag == 1) as when:
            # type checker will scream here unfortunately,
            # use f[int, uint16, BigEndian, when] instead
            value: when[f[int, uint16, BigEndian]]
        trailer: f[int, uint8]

    assert pack(Packet(flag=1, value=0x0102, trailer=0xFF)) == b"\x01\x01\x02\xff"
    assert unpack(Packet, b"\x01\x01\x02\xff") == Packet(
        flag=1, value=0x0102, trailer=0xFF
    )
    assert pack(Packet(flag=0, value=0x0102, trailer=0xFF)) == b"\x00\xff"


def test_marker_if_alias_unpacks_true_branch():
    OptionalByte = define_marker_optional_byte()

    decoded = unpack(OptionalByte, b"\x01\xaa\xff")

    assert not hasattr(OptionalByte, "when")
    assert not hasattr(OptionalByte, "_")
    assert not hasattr(OptionalByte, "_end")
    assert decoded.flag == 1
    assert decoded.value == 0xAA
    assert decoded.trailer == 0xFF


def test_marker_if_alias_false_branch():
    OptionalByte = define_marker_optional_byte()

    decoded = unpack(OptionalByte, b"\x00\xff")

    assert decoded.flag == 0
    assert decoded.value is None
    assert decoded.trailer == 0xFF
    assert pack(OptionalByte(flag=0, value=0xAA, trailer=0xFF)) == b"\x00\xff"


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="inline conditional metadata is a 3.14 path"
)
def test_inline_metadata_if_alias_unpacks_true_branch_without_marker_fields():
    OptionalByte = define_inline_optional_byte()

    decoded = unpack(OptionalByte, b"\x01\xaa\xff")

    assert not hasattr(OptionalByte, "when")
    assert decoded.flag == 1
    assert decoded.value == 0xAA
    assert decoded.trailer == 0xFF


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="inline conditional metadata is a 3.14 path"
)
def test_inline_metadata_if_alias_false_branch_consumes_no_bytes():
    OptionalByte = define_inline_optional_byte()

    decoded = unpack(OptionalByte, b"\x00\xff")

    assert decoded.flag == 0
    assert decoded.value is None
    assert decoded.trailer == 0xFF
    assert pack(OptionalByte(flag=0, value=0xAA, trailer=0xFF)) == b"\x00\xff"


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="inline conditional metadata is a 3.14 path"
)
def test_inline_start_end_cover_multi_field_block_without_marker_fields():
    @struct
    class Packet:
        flag: f[int, uint8]
        with If(this.flag == 1) as when:
            first: f[int, uint8, Start(when)]
            second: f[int, uint16]
            third: f[int, uint8, End(when)]
        trailer: f[int, uint8]

    assert not hasattr(Packet, "when")

    decoded = unpack(Packet, b"\x01\xa1\x03\x02\xa3\xff")
    assert (
        decoded.flag,
        decoded.first,
        decoded.second,
        decoded.third,
        decoded.trailer,
    ) == (1, 0xA1, 0x0203, 0xA3, 0xFF)

    decoded = unpack(Packet, b"\x00\xff")
    assert (
        decoded.flag,
        decoded.first,
        decoded.second,
        decoded.third,
        decoded.trailer,
    ) == (0, None, None, None, 0xFF)
    assert pack(Packet(flag=0, first=1, second=2, third=3, trailer=0xFF)) == b"\x00\xff"


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="inline conditional metadata is a 3.14 path"
)
def test_inline_start_requires_end_marker():
    with pytest.raises(StructException, match="missing an End\\(when\\) marker"):

        @struct
        class Packet:
            flag: f[int, uint8]
            with If(this.flag == 1) as when:
                value: f[int, uint8, Start(when)]
            trailer: f[int, uint8]


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="inline conditional metadata is a 3.14 path"
)
def test_inline_end_requires_start_marker():
    with pytest.raises(StructException, match="has no matching start marker"):

        @struct
        class Packet:
            flag: f[int, uint8]
            with If(this.flag == 1) as when:
                value: f[int, uint8, End(when)]
            trailer: f[int, uint8]


def test_marker_if_alias_preserves_annotated_options():
    @struct(order=LittleEndian)
    class Packet:
        flag: f[int, uint8]
        with If(this.flag == 1) as when:
            _: f[None, when] = Invisible()
            value: f[int, uint16, BigEndian]
            _end: f[None, End(when)] = Invisible()
        trailer: f[int, uint8]

    assert pack(Packet(flag=1, value=0x0102, trailer=0xFF)) == b"\x01\x01\x02\xff"
    assert unpack(Packet, b"\x01\x01\x02\xff") == Packet(
        flag=1, value=0x0102, trailer=0xFF
    )
    assert pack(Packet(flag=0, value=0x0102, trailer=0xFF)) == b"\x00\xff"


def test_marker_multiple_if_blocks_are_independent():
    @struct
    class Packet:
        flag: f[int, uint8]
        with If(this.flag == 1) as when1:
            _: f[None, when1] = Invisible()
            first: f[int, uint8]
            _end: f[None, End(when1)] = Invisible()
        with If(this.flag == 2) as when2:
            _2: f[None, when2] = Invisible()
            second: f[int, uint8]
            _end2: f[None, End(when2)] = Invisible()
        trailer: f[int, uint8]

    decoded = unpack(Packet, b"\x01\xa1\xff")
    assert (decoded.flag, decoded.first, decoded.second, decoded.trailer) == (
        1,
        0xA1,
        None,
        0xFF,
    )
    decoded = unpack(Packet, b"\x02\xb2\xff")
    assert (decoded.flag, decoded.first, decoded.second, decoded.trailer) == (
        2,
        None,
        0xB2,
        0xFF,
    )
    decoded = unpack(Packet, b"\x00\xff")
    assert (decoded.flag, decoded.first, decoded.second, decoded.trailer) == (
        0,
        None,
        None,
        0xFF,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 14),
    reason="lazy annotations make repeated marker aliases observable",
)
def test_py314_rejects_reused_marker_alias():
    with pytest.raises(StructException, match="reuses a marker alias"):

        @struct
        class Packet:
            flag: f[int, uint8]
            with If(this.flag == 1) as when:
                _: f[None, when] = Invisible()
                first: f[int, uint8]
                _end: f[None, End(when)] = Invisible()
            with If(this.flag == 2) as when:
                _2: f[None, when] = Invisible()
                second: f[int, uint8]
                _end2: f[None, End(when)] = Invisible()
            trailer: f[int, uint8]


def test_marker_nested_if_blocks_combine_conditions():
    @struct
    class Packet:
        flag: f[int, uint8]
        kind: f[int, uint8]
        with If(this.flag == 1) as outer:
            _: f[None, outer] = Invisible()
            with If(this.kind == 2) as inner:
                _1: f[None, inner] = Invisible()
                value: f[int, uint8]
                _end1: f[None, End(inner)] = Invisible()
            _end: f[None, End(outer)] = Invisible()
        trailer: f[int, uint8]

    decoded = unpack(Packet, b"\x00\x02\xff")
    assert (decoded.flag, decoded.kind, decoded.value, decoded.trailer) == (
        0,
        2,
        None,
        0xFF,
    )
    decoded = unpack(Packet, b"\x01\x02\xaa\xff")
    assert (decoded.flag, decoded.kind, decoded.value, decoded.trailer) == (
        1,
        2,
        0xAA,
        0xFF,
    )
    decoded = unpack(Packet, b"\x01\x03\xff")
    assert (decoded.flag, decoded.kind, decoded.value, decoded.trailer) == (
        1,
        3,
        None,
        0xFF,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 14),
    reason="duplicate marker behavior differs before lazy annotations",
)
def test_py314_marker_if_rejects_duplicate_field_names_with_branch_guidance():
    with pytest.raises(StructException, match="use Branch"):

        @struct
        class Packet:
            tag: f[int, uint8]
            with If(this.tag == 1) as when1:
                _: f[None, when1] = Invisible()
                value: f[int, uint8]
                _end: f[None, End(when1)] = Invisible()
            with If(this.tag == 2) as when2:
                _2: f[None, when2] = Invisible()
                value: f[int, uint16]
                _end2: f[None, End(when2)] = Invisible()
            trailer: f[int, uint8]


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="explicit marker ElseIf is a 3.14 path"
)
def test_py314_marker_elseif_and_else_chain_distinct_fields():
    @struct
    class Packet:
        tag: f[int, uint8]
        with If(this.tag == 1) as first:
            _: f[None, first] = Invisible()
            a: f[int, uint8]
            _end: f[None, End(first)] = Invisible()
        with ElseIf(first, this.tag == 2) as second:
            _2: f[None, second] = Invisible()
            b: f[int, uint8]
            _end2: f[None, End(second)] = Invisible()
        with Else(second) as fallback:
            _3: f[None, fallback] = Invisible()
            c: f[int, uint8]
            _end3: f[None, End(fallback)] = Invisible()
        trailer: f[int, uint8]

    decoded = unpack(Packet, b"\x01\xa1\xff")
    assert (decoded.tag, decoded.a, decoded.b, decoded.c, decoded.trailer) == (
        1,
        0xA1,
        None,
        None,
        0xFF,
    )
    decoded = unpack(Packet, b"\x02\xb2\xff")
    assert (decoded.tag, decoded.a, decoded.b, decoded.c, decoded.trailer) == (
        2,
        None,
        0xB2,
        None,
        0xFF,
    )
    decoded = unpack(Packet, b"\x03\xc3\xff")
    assert (decoded.tag, decoded.a, decoded.b, decoded.c, decoded.trailer) == (
        3,
        None,
        None,
        0xC3,
        0xFF,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="inline conditional metadata is a 3.14 path"
)
def test_py314_inline_elseif_and_else_chain_distinct_fields():
    @struct
    class Packet:
        tag: f[int, uint8]
        with If(this.tag == 1) as first:
            a: f[int, uint8, first]
        with ElseIf(first, this.tag == 2) as second:
            b: f[int, uint8, second]
        with Else(second) as fallback:
            c: f[int, uint8, fallback]
        trailer: f[int, uint8]

    decoded = unpack(Packet, b"\x01\xa1\xff")
    assert (decoded.tag, decoded.a, decoded.b, decoded.c, decoded.trailer) == (
        1,
        0xA1,
        None,
        None,
        0xFF,
    )
    decoded = unpack(Packet, b"\x02\xb2\xff")
    assert (decoded.tag, decoded.a, decoded.b, decoded.c, decoded.trailer) == (
        2,
        None,
        0xB2,
        None,
        0xFF,
    )
    decoded = unpack(Packet, b"\x03\xc3\xff")
    assert (decoded.tag, decoded.a, decoded.b, decoded.c, decoded.trailer) == (
        3,
        None,
        None,
        0xC3,
        0xFF,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="explicit marker ElseIf is a 3.14 path"
)
def test_py314_marker_rejects_elseif_after_else():
    with pytest.raises(StructException, match="after Else"):

        @struct
        class Packet:
            tag: f[int, uint8]
            with If(this.tag == 1) as first:
                _: f[None, first] = Invisible()
                a: f[int, uint8]
                _end: f[None, End(first)] = Invisible()
            with Else(first) as fallback:
                _2: f[None, fallback] = Invisible()
                b: f[int, uint8]
                _end2: f[None, End(fallback)] = Invisible()
            with ElseIf(fallback, this.tag == 3) as third:
                _3: f[None, third] = Invisible()
                c: f[int, uint8]
                _end3: f[None, End(third)] = Invisible()


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="legacy ElseIf still works before 3.14"
)
def test_py314_legacy_elseif_fails_with_clear_message():
    with pytest.raises(StructException, match="ElseIf\\(previous, condition\\)"):

        @struct
        class Packet:
            tag: f[int, uint8]
            with If(this.tag == 1) as when:
                _: f[None, when] = Invisible()
                value: f[int, uint8]
                _end: f[None, End(when)] = Invisible()
            with ElseIf(this.tag == 2):
                other: f[int, uint8]
            trailer: f[int, uint8]


def test_branch_same_field_chain_unpack_and_pack():
    @struct
    class Packet:
        tag: f[int, uint8]
        value: f[
            int,
            Branch(
                When(this.tag == 1, uint8),
                When(this.tag == 2, uint16),
                Otherwise(uint8),
            ),
        ]
        trailer: f[int, uint8]

    decoded = unpack(Packet, b"\x01\xaa\xff")
    assert (decoded.tag, decoded.value, decoded.trailer) == (1, 0xAA, 0xFF)
    decoded = unpack(Packet, b"\x02\x02\x01\xff")
    assert (decoded.tag, decoded.value, decoded.trailer) == (2, 0x0102, 0xFF)
    decoded = unpack(Packet, b"\x03\xcc\xff")
    assert (decoded.tag, decoded.value, decoded.trailer) == (3, 0xCC, 0xFF)

    assert pack(Packet(tag=1, value=0xAA, trailer=0xFF)) == b"\x01\xaa\xff"
    assert pack(Packet(tag=2, value=0x0102, trailer=0xFF)) == b"\x02\x02\x01\xff"
    assert pack(Packet(tag=3, value=0xCC, trailer=0xFF)) == b"\x03\xcc\xff"


def test_branch_arm_preserves_annotated_options():
    @struct(order=LittleEndian)
    class Packet:
        tag: f[int, uint8]
        value: f[
            int,
            Branch(
                When(this.tag == 1, f[int, uint16, BigEndian]),
                Otherwise(uint16),
            ),
        ]
        trailer: f[int, uint8]

    assert pack(Packet(tag=1, value=0x0102, trailer=0xFF)) == b"\x01\x01\x02\xff"
    assert pack(Packet(tag=0, value=0x0102, trailer=0xFF)) == b"\x00\x02\x01\xff"


def test_marker_if_requires_end_marker():
    with pytest.raises(StructException, match="missing an End\\(when\\) marker"):

        @struct
        class Packet:
            flag: f[int, uint8]
            with If(this.flag == 1) as when:
                _: f[None, when] = Invisible()
                value: f[int, uint8]
            trailer: f[int, uint8]


def test_marker_if_rejects_end_without_start_marker():
    with pytest.raises(StructException, match="has no matching start marker"):

        @struct
        class Packet:
            flag: f[int, uint8]
            with If(this.flag == 1) as when:
                _end: f[None, End(when)] = Invisible()
                value: f[int, uint8]
            trailer: f[int, uint8]


@pytest.mark.skipif(
    sys.version_info < (3, 14), reason="implicit If still uses legacy annotations"
)
def test_implicit_if_on_python314_requires_explicit_alias():
    with pytest.raises(StructException, match="with If\\(condition\\) as when"):

        @struct
        class Packet:
            flag: f[int, uint8]
            with If(this.flag == 1):
                value: f[int, uint8]
            trailer: f[int, uint8]
