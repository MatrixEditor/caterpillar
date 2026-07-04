# Copyright (C) MatrixEditor 2023-2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# pyright: basic
import pytest

import caterpillar
from caterpillar.context import O_CONTEXT_FACTORY

try:
    from examples.comparison import comparison_1_caterpillar as caterpillar_default

    pytestmark = pytest.mark.benchmark

except ImportError:
    caterpillar_default = None


NATIVE_ONLY = pytest.mark.skipif(
    not caterpillar.native_support(), reason="native extension unavailable"
)
HAVE_EXAMPLES = pytest.mark.skipif(
    caterpillar_default is None, reason="examples unavailable"
)

ROUNDS = 10
ITEM_COUNT = 1000


def _make_default_items(count: int):
    return [
        caterpillar_default.Item(
            i & 0xFF,
            (i * 17) & 0xFFFFFF,
            caterpillar_default.Flags(bool(i & 1), i & 0x07),
            [i & 0xFF, (i + 1) & 0xFF, (i + 2) & 0xFF],
            "...",
            "...",
        )
        for i in range(count)
    ]


if caterpillar_default is not None:
    DEFAULT_ITEMS = _make_default_items(ITEM_COUNT)
    COMPARISON_RAW = caterpillar_default.pack(DEFAULT_ITEMS, caterpillar_default.Format)


def _bench(benchmark, fn, validate=None):
    result = benchmark.pedantic(fn, rounds=ROUNDS, iterations=10)
    if validate is not None:
        validate(result)
    return result


def _assert_caterpillar_items(items):
    assert len(items) == ITEM_COUNT
    assert items[0].name1 == "..."
    assert items[-1].fixedarray1 == [
        (ITEM_COUNT - 1) & 0xFF,
        ITEM_COUNT & 0xFF,
        (ITEM_COUNT + 1) & 0xFF,
    ]


def _assert_raw(data):
    assert data == COMPARISON_RAW


def _assert_mapping_count(obj):
    assert obj["count"] == ITEM_COUNT


def _assert_attr_count(obj):
    assert obj.count == ITEM_COUNT


def _assert_bytes(data):
    assert isinstance(data, bytes | bytearray)


def _assert_hachoir_count(fields):
    assert fields[0].value == ITEM_COUNT


@HAVE_EXAMPLES
def test_bench_caterpillar_unpack(benchmark):
    _bench(
        benchmark,
        lambda: caterpillar_default.unpack(caterpillar_default.Format, COMPARISON_RAW),
        _assert_caterpillar_items,
    )


@HAVE_EXAMPLES
def test_bench_caterpillar_pack(benchmark):
    _bench(
        benchmark,
        lambda: caterpillar_default.pack(DEFAULT_ITEMS, caterpillar_default.Format),
        _assert_raw,
    )


@HAVE_EXAMPLES
@NATIVE_ONLY
def test_bench_caterpillar_c_context_default_unpack(benchmark):
    from caterpillar.c import c_Context

    old_factory = O_CONTEXT_FACTORY.value
    O_CONTEXT_FACTORY.value = c_Context
    try:
        _bench(
            benchmark,
            lambda: caterpillar_default.unpack(
                caterpillar_default.Format, COMPARISON_RAW
            ),
            _assert_caterpillar_items,
        )
    finally:
        O_CONTEXT_FACTORY.value = old_factory


@HAVE_EXAMPLES
@NATIVE_ONLY
def test_bench_caterpillar_c_context_default_pack(benchmark):
    from caterpillar.c import c_Context

    old_factory = O_CONTEXT_FACTORY.value
    O_CONTEXT_FACTORY.value = c_Context
    try:
        _bench(
            benchmark,
            lambda: caterpillar_default.pack(DEFAULT_ITEMS, caterpillar_default.Format),
            _assert_raw,
        )
    finally:
        O_CONTEXT_FACTORY.value = old_factory


@HAVE_EXAMPLES
@NATIVE_ONLY
def test_bench_caterpillar_c_classes_unpack(benchmark):
    from examples.comparison import comparison_1_caterpillar_c as caterpillar_c

    _bench(
        benchmark,
        lambda: caterpillar_c.unpack(caterpillar_c.Format, COMPARISON_RAW),
        _assert_caterpillar_items,
    )


@HAVE_EXAMPLES
@NATIVE_ONLY
def test_bench_caterpillar_c_classes_pack(benchmark):
    from examples.comparison import comparison_1_caterpillar_c as caterpillar_c

    c_items = [
        caterpillar_c.Item(
            i & 0xFF,
            (i * 17) & 0xFFFFFF,
            caterpillar_c.Flags(bool(i & 1), i & 0x07),
            [i & 0xFF, (i + 1) & 0xFF, (i + 2) & 0xFF],
            "...",
            "...",
        )
        for i in range(ITEM_COUNT)
    ]

    _bench(
        benchmark,
        lambda: caterpillar_c.pack(c_items, caterpillar_c.Format),
        _assert_raw,
    )


@HAVE_EXAMPLES
@NATIVE_ONLY
def test_bench_caterpillar_c_context_unpack(benchmark):
    from caterpillar.c import c_Context
    from examples.comparison import comparison_1_caterpillar_c as caterpillar_c

    old_factory = O_CONTEXT_FACTORY.value
    O_CONTEXT_FACTORY.value = c_Context
    try:
        _bench(
            benchmark,
            lambda: caterpillar_c.unpack(caterpillar_c.Format, COMPARISON_RAW),
            _assert_caterpillar_items,
        )
    finally:
        O_CONTEXT_FACTORY.value = old_factory


@HAVE_EXAMPLES
@NATIVE_ONLY
def test_bench_caterpillar_c_context_pack(benchmark):
    from caterpillar.c import c_Context
    from examples.comparison import comparison_1_caterpillar_c as caterpillar_c

    c_items = [
        caterpillar_c.Item(
            i & 0xFF,
            (i * 17) & 0xFFFFFF,
            caterpillar_c.Flags(bool(i & 1), i & 0x07),
            [i & 0xFF, (i + 1) & 0xFF, (i + 2) & 0xFF],
            "...",
            "...",
        )
        for i in range(ITEM_COUNT)
    ]

    old_factory = O_CONTEXT_FACTORY.value
    O_CONTEXT_FACTORY.value = c_Context
    try:
        _bench(
            benchmark,
            lambda: caterpillar_c.pack(c_items, caterpillar_c.Format),
            _assert_raw,
        )
    finally:
        O_CONTEXT_FACTORY.value = old_factory


@HAVE_EXAMPLES
def test_bench_construct_parse(benchmark):
    construct_comparison = pytest.importorskip(
        "examples.comparison.comparison_1_construct"
    )

    _bench(
        benchmark,
        lambda: construct_comparison.d.parse(COMPARISON_RAW),
        _assert_mapping_count,
    )


@HAVE_EXAMPLES
def test_bench_construct_build(benchmark):
    construct_comparison = pytest.importorskip(
        "examples.comparison.comparison_1_construct"
    )
    obj = construct_comparison.d.parse(COMPARISON_RAW)

    _bench(
        benchmark,
        lambda: construct_comparison.d.build(obj),
        _assert_raw,
    )


@HAVE_EXAMPLES
def test_bench_construct_compiled_parse(benchmark):
    construct_comparison = pytest.importorskip(
        "examples.comparison.comparison_1_construct"
    )

    _bench(
        benchmark,
        lambda: construct_comparison.d_compiled.parse(COMPARISON_RAW),
        _assert_mapping_count,
    )


@HAVE_EXAMPLES
def test_bench_construct_compiled_build(benchmark):
    construct_comparison = pytest.importorskip(
        "examples.comparison.comparison_1_construct"
    )
    obj = construct_comparison.d.parse(COMPARISON_RAW)

    _bench(
        benchmark,
        lambda: construct_comparison.d_compiled.build(obj),
        _assert_raw,
    )


@HAVE_EXAMPLES
def test_bench_kaitai_parse(benchmark):
    kaitai_comparison = pytest.importorskip("examples.comparison.comparison_1_kaitai")

    _bench(
        benchmark,
        lambda: kaitai_comparison.Comparison1Kaitai.from_bytes(COMPARISON_RAW),
        _assert_attr_count,
    )


@HAVE_EXAMPLES
def test_bench_hachoir_parse(benchmark):
    hachoir_comparison = pytest.importorskip("examples.comparison.comparison_1_hachoir")
    hachoir_stream = pytest.importorskip("hachoir.stream")

    _bench(
        benchmark,
        lambda: list(
            hachoir_comparison.Format(hachoir_stream.StringInputStream(COMPARISON_RAW))
        ),
        _assert_hachoir_count,
    )


@HAVE_EXAMPLES
def test_bench_mrcrowbar_parse(benchmark):
    mrcrowbar_comparison = pytest.importorskip(
        "examples.comparison.comparison_1_mrcrowbar"
    )

    _bench(
        benchmark,
        lambda: mrcrowbar_comparison.Format(COMPARISON_RAW),
        _assert_attr_count,
    )


@HAVE_EXAMPLES
def test_bench_mrcrowbar_build(benchmark):
    mrcrowbar_comparison = pytest.importorskip(
        "examples.comparison.comparison_1_mrcrowbar"
    )
    obj = mrcrowbar_comparison.Format(COMPARISON_RAW)

    _bench(
        benchmark,
        obj.export_data,
        _assert_bytes,
    )
