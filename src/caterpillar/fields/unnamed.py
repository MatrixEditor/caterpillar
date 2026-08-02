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
import re
from io import BytesIO
from typing import TYPE_CHECKING, Annotated, Any, Generic, get_args, get_origin

from typing_extensions import TypeVarTuple, Unpack, override

from caterpillar._common import WithoutContextVar, read_exact
from caterpillar.abc import (
    _AnnotationT,
    _ArchLike,
    _ContextLambda,
    _ContextLike,
    _EndianLike,
    _StructLike,
)
from caterpillar.byteorder import ByteOrder, DynByteOrder
from caterpillar.context import (
    CTX_ARCH,
    CTX_FIELD,
    CTX_ORDER,
    CTX_PATH,
    CTX_SEQ,
    CTX_STREAM,
    O_CONTEXT_FACTORY,
    Context,
)
from caterpillar.exception import ValidationError
from caterpillar.fields import Field
from caterpillar.registry import TypeConverter, annotation_registry, to_struct
from caterpillar.shared import getstruct

from ._mixin import FieldStruct

__all__ = [
    "Unnamed",
    "sized",
]

_Tys = TypeVarTuple("_Tys")

# Matches the "._<number>" convenience attribute access, e.g. "_0", "_12".
_ATTR_RE = re.compile(r"^_([0-9]+)$")


def _resolve_member(annotation: _AnnotationT) -> _StructLike[Any, Any]:
    """
    Resolve a single ``Unnamed`` member annotation into a ``_StructLike``.
    """
    if get_origin(annotation) is Annotated:
        _, struct_obj, *_ = get_args(annotation)
        annotation = struct_obj
    return to_struct(getstruct(annotation, annotation))


class UnnamedAlias(Generic[Unpack[_Tys]]):
    """
    Lightweight marker object produced by ``Unnamed[...]``.

    This is *not* a ``_StructLike`` itself - :class:`_UnnamedTypeConverter`
    is what turns it into a real, usable struct (:class:`UnnamedStruct`)
    once it is encountered as a field annotation.
    """

    __slots__: tuple[str, ...] = ("length", "member_annotations")

    def __init__(
        self,
        member_annotations: tuple[_AnnotationT, ...],
        length: "_ContextLambda[int] | int | None" = None,
    ) -> None:
        self.member_annotations: tuple[_AnnotationT, ...] = member_annotations
        self.length: _ContextLambda[int] | int | None = length

    def sized(
        self, length: "_ContextLambda[int] | int"
    ) -> "UnnamedAlias[Unpack[_Tys]]":
        """Override the default (max-of-members) size for this field."""
        return UnnamedAlias(self.member_annotations, length)


class UnnamedStruct(
    FieldStruct["Unnamed[Unpack[_Tys]]", "Unnamed[Unpack[_Tys]]"], Generic[Unpack[_Tys]]
):
    """The real ``_StructLike`` behind an ``Unnamed[...]`` field."""

    __slots__: tuple[str, ...] = ("length", "members")

    def __init__(
        self,
        members: tuple[_StructLike[Any, Any], ...],
        length: "_ContextLambda[int] | int | None",
    ) -> None:
        self.members: tuple[_StructLike[Any, Any], ...] = members
        self.length: _ContextLambda[int] | int | None = length

    def __type__(self) -> type:
        return Unnamed

    def __size__(self, context: _ContextLike) -> int:
        if self.length is not None:
            return self.length(context) if callable(self.length) else self.length

        sizes = [m.__size__(context) for m in self.members]
        if any(s is Ellipsis for s in sizes):
            raise ValidationError(
                "Unnamed members must have a fixed size unless an "
                + "explicit size is given via .sized(...)",
                context,
            )
        return max(sizes)

    @override
    def unpack_single(self, context: _ContextLike) -> "Unnamed[Unpack[_Tys]]":
        root: _ContextLike = context._root
        field: Field | None = context.get(CTX_FIELD)
        order: _EndianLike | None = (
            field.order
            if field is not None and field.has_order()
            else context.get(CTX_ORDER, root.get(CTX_ORDER))
        )
        if isinstance(order, DynByteOrder):
            order = ByteOrder(order.name, order.getch(context))

        arch: _ArchLike | None = context.get(CTX_ARCH, root.get(CTX_ARCH))
        path: str = context[CTX_PATH]
        size = self.__size__(context)
        raw = read_exact(context, size, "Unnamed field")
        return Unnamed.from_raw(self.members, raw, order, arch, path)

    @override
    def pack_single(self, obj: "Unnamed[Unpack[_Tys]]", context: _ContextLike) -> None:
        size = self.__size__(context)
        stream = context[CTX_STREAM]

        if obj._raw is not None:
            data = obj._raw  # pyright: ignore[reportPrivateUsage]
            if len(data) != size:
                raise ValidationError(
                    f"Unnamed field expected {size} bytes, got {len(data)}",
                    context,
                )
            stream.write(data)
            return

        if obj._active_index is None:  # pyright: ignore[reportPrivateUsage]
            raise ValidationError(
                "Packing a fresh Unnamed requires at least one member "
                + "value to be set, e.g. Unnamed(value) or "
                + "Unnamed(_2=value)",
                context,
            )

        index = obj._active_index  # pyright: ignore[reportPrivateUsage]
        if not (0 <= index < len(self.members)):
            raise ValidationError(
                f"member index {index} is out of range for this Unnamed "
                + f"field (0-{len(self.members) - 1})",
                context,
            )
        value = obj._cache[index]  # pyright: ignore[reportPrivateUsage]
        member = self.members[index]
        buf = BytesIO()
        with (
            WithoutContextVar(context, CTX_STREAM, buf),
            WithoutContextVar(context, CTX_SEQ, False),
        ):
            member.__pack__(value, context)
        data = buf.getvalue()
        if len(data) > size:
            raise ValidationError(
                f"encoded member {index} does not fit in {size} bytes (got {len(data)})",
                context,
            )
        stream.write(data.ljust(size, b"\x00"))


class _SizedMarker:
    """
    Internal, dedicated marker produced by :class:`sized`.
    """

    __slots__: tuple[str, ...] = ("length",)

    def __init__(self, length: "_ContextLambda[int] | int") -> None:
        self.length: _ContextLambda[int] | int = length

    @override
    def __repr__(self) -> str:
        return f"sized[{self.length!r}]"


class sized:
    """
    Inline marker for a fixed (or context-lambda) size, usable as the last
    argument of :class:`Unnamed`'s subscript::

        payload: Unnamed[uint8_t, uint16_t, sized[10]]

    which is a runtime-equivalent shorthand for::

        payload: Unnamed[uint8_t, uint16_t].sized(10)

    .. warning::
        ``sized[...]`` occupies one of ``Unnamed``'s generic positions, so
        static type checkers count it as an extra member type

    At most one ``sized[...]`` marker may appear in ``Unnamed[...]``, and it
    must be the last argument.
    """

    def __class_getitem__(cls, length: "_ContextLambda[int] | int") -> _SizedMarker:
        return _SizedMarker(length)


class Unnamed(tuple[Unpack[_Tys]], Generic[Unpack[_Tys]]):
    """
    A fixed-size, lazily-decoded, positional view over a shared byte window.

    Instances are normally produced by unpacking an ``Unnamed[...]``-typed
    field. Individual members are decoded (and cached) on first access via
    ``value[i]`` or ``value._i``.

    Fresh instances may also be constructed directly for packing purposes,
    without a prior unpack:

    >>> Unnamed()                  # nothing assigned yet
    Unnamed()
    >>> Unnamed(1, 2, 3)           # positional: index 0, 1, 2
    Unnamed(1, 2, 3)
    >>> Unnamed(_3=0xBEEF)         # keyword: only index 3 is set
    Unnamed(?, ?, ?, 48879)

    Since all members share the exact same bytes, only one member can ever
    be *packed*: whichever index was assigned last (in call order) is the
    one actually encoded. Assigning the same index twice in one call is
    an error.
    """

    if TYPE_CHECKING:

        @classmethod
        def sized(
            cls, length: _ContextLambda[int] | int
        ) -> "Unnamed[Unpack[_Tys]]": ...

    _raw: bytes | None
    _members: tuple[_StructLike[Any, Any], ...] | None
    _order: _EndianLike | None
    _arch: _ArchLike | None
    _path: str
    _cache: dict[int, Any]
    _active_index: int | None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Unnamed[Unpack[_Tys]]":
        self = tuple.__new__(cls, ())
        self._raw = None
        self._members = None
        self._order = None
        self._arch = None
        self._path = ""
        self._cache = {}
        # Index of the member that was assigned last (in call order) -
        # this is the one that gets packed when there is no raw data yet.
        self._active_index = None

        for index, value in enumerate(args):
            self._cache[index] = value
            self._active_index = index

        for key, value in kwargs.items():
            m = _ATTR_RE.match(key)
            if not m:
                raise TypeError(
                    f"{cls.__name__}() got an unexpected keyword argument "
                    + f"{key!r} (expected e.g. _0, _1, ...)"
                )
            index = int(m.group(1))
            if index in self._cache:
                raise TypeError(
                    f"{cls.__name__}() got multiple values for index {index}"
                )
            self._cache[index] = value
            self._active_index = index

        return self

    @classmethod
    def from_raw(
        cls,
        members: tuple[_StructLike[Any, Any], ...],
        raw: bytes,
        order: "_EndianLike | None",
        arch: "_ArchLike | None",
        path: str,
    ) -> "Unnamed[Unpack[_Tys]]":
        self = tuple.__new__(cls, ())
        self._raw = raw
        self._members = members
        self._order = order
        self._arch = arch
        self._path = path
        self._cache = {}
        self._active_index = None
        return self

    @override
    def __len__(self) -> int:
        if self._members is not None:
            return len(self._members)
        if self._cache:
            return max(self._cache) + 1
        return 0

    def get(self, index: int) -> Any:
        assert self._members is not None and self._raw is not None
        member = self._members[index]
        factory = O_CONTEXT_FACTORY.value or Context
        fresh_context = factory(
            _io=BytesIO(self._raw),
            _is_seq=False,
            _order=self._order,
            _arch=self._arch,
            _path=f"{self._path}[{index}]",
        )
        return member.__unpack__(fresh_context)

    @override
    def __getitem__(self, index: Any) -> Any:
        if isinstance(index, slice):
            return tuple(self[i] for i in range(*index.indices(len(self))))

        n = len(self)
        i = index + n if index < 0 else index
        if not (0 <= i < n):
            raise IndexError(index)

        if i in self._cache:
            return self._cache[i]

        if self._raw is None:
            raise AttributeError(
                f"member {i} was not assigned on this Unnamed and "
                + "there is no raw data available to decode it from"
            )

        value = self.get(i)
        self._cache[i] = value
        return value

    @override
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getattr__(self, name: str) -> Any:
        m = _ATTR_RE.match(name)
        if not m:
            raise AttributeError(name)
        return self[int(m.group(1))]

    @override
    def __repr__(self) -> str:
        n = len(self)
        parts = (repr(self._cache[i]) if i in self._cache else "?" for i in range(n))
        return f"Unnamed({', '.join(parts)})"

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unnamed):
            return NotImplemented
        if self._raw is not None and other._raw is not None:
            return self._raw == other._raw
        return len(self) == len(other) and all(
            self[i] == other[i] for i in range(len(self))
        )

    @override
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    @override
    def __hash__(self) -> int:
        if self._raw is not None:
            return hash(self._raw)
        return hash(tuple(self))

    def __class_getitem__(cls, args: object) -> UnnamedAlias:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not isinstance(args, tuple):
            args = (args,)
        if not args:
            raise TypeError("Unnamed[...] requires at least one member type")

        length: _ContextLambda[int] | int | None = None
        marker_count = sum(1 for a in args if isinstance(a, _SizedMarker))
        if marker_count:
            last = args[-1]
            if marker_count > 1 or not isinstance(last, _SizedMarker):
                raise TypeError(
                    "Unnamed[...] accepts at most one sized[...] marker, "
                    + "and it must be the last argument"
                )
            length = last.length
            args = args[:-1]
            if not args:
                raise TypeError(
                    "Unnamed[...] requires at least one member type "
                    + "(besides the trailing sized[...] marker)"
                )

        return UnnamedAlias(args, length)


class _UnnamedTypeConverter(TypeConverter):
    @override
    def matches(self, annotation: object) -> bool:
        return isinstance(annotation, UnnamedAlias)

    @override
    def convert(
        self, annotation: object, kwargs: dict[str, Any]
    ) -> _StructLike[Any, Any]:
        assert isinstance(annotation, UnnamedAlias)
        members = tuple(_resolve_member(a) for a in annotation.member_annotations)
        return UnnamedStruct(members, annotation.length)


annotation_registry.insert(0, _UnnamedTypeConverter())
