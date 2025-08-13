# Copyright (C) MatrixEditor 2023-2025
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
import types
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    TypeVar,
    Union,
    Type,
    Generic,
    overload,
)

from caterpillar import registry
from caterpillar.abc import (
    _ContainsStruct,
    _OT,
    _IT,
    _SupportsPack,
    _StreamType,
    _SupportsUnpack,
    _ContextLike,
    _StructLike,
    _SupportsSize,
    _OptionLike,
)
from caterpillar.byteorder import Arch, ByteOrder
from caterpillar.fields._base import Field
from caterpillar.model._base import Sequence

_ModelT = TypeVar("_ModelT")

class Struct(Sequence[_ModelT]):
    kw_only: bool
    model: type[_ModelT]
    def __init__(
        self,
        model: type[_ModelT],
        options: Iterable[_OptionLike] | None = None,
        order: ByteOrder | None = None,
        arch: Arch | None = None,
        field_options: _OptionLike | None = None,
        kw_only: bool = False,
        hook_cls: type[_UnionHookLike[_ModelT]] | None = None,
    ) -> None: ...
    def __type__(self) -> type[_ModelT]: ...
    def unpack_one(self, context: _ContextLike) -> _ModelT: ...
    def get_value(self, obj: Any, name: str, field: Field) -> Any | None: ...

class _StructTypeConverter(registry.TypeConverter):
    def __init__(self) -> None: ...
    def matches(self, annotation: Any) -> bool: ...
    def convert(self, annotation: Any, kwargs: dict[str, Any]) -> Struct[Any]: ...

class _UnionHookLike(Generic[_ModelT]):
    def __model_init__(self, obj: _ModelT, *args, **kwargs) -> None: ...
    def __model_setattr__(self, obj: _ModelT, key: str, new_value: Any) -> None: ...

class UnionHook(Generic[_ModelT]):
    struct: Struct[_ModelT]
    max_size: int
    def __init__(self, struct_: Struct[_ModelT]) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def __model_init__(self, obj: Any, *args, **kwargs) -> None: ...
    def __model_setattr__(self, obj: Any, key: str, new_value: Any) -> None: ...
    def refresh(
        self, obj: Any, key: str, new_value: Any, members: dict[str, Field]
    ) -> None: ...

@overload
def struct(
    cls: type[_ModelT],
    /,
    *,
    options: Optional[Iterable[_OptionLike]] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Optional[Iterable[_OptionLike]] = None,
    kw_only: bool = False,
) -> type[_ModelT]: ...
@overload
def struct(
    cls: None = None,
    /,
    *,
    options: Optional[Iterable[_OptionLike]] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Optional[Iterable[_OptionLike]] = None,
    kw_only: bool = False,
) -> Callable[[_ModelT], _ModelT]: ...
@overload
def union(
    cls: type[_ModelT],
    /,
    *,
    options: Optional[Iterable[_OptionLike]] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Optional[Iterable[_OptionLike]] = None,
    kw_only: bool = False,
    hook_cls: Optional[type[_UnionHookLike[_ModelT]]] = None,
) -> type[_ModelT]: ...
@overload
def union(
    cls: None = None,
    /,
    *,
    options: Optional[Iterable[_OptionLike]] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Optional[Iterable[_OptionLike]] = None,
    kw_only: bool = False,
    hook_cls: Optional[type[_UnionHookLike[_ModelT]]] = None,
) -> Callable[[_ModelT], _ModelT]: ...
@overload
def pack(
    obj: _ContainsStruct[_ModelT, _ModelT],
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    **kwds,
) -> bytes: ...
@overload
def pack(
    obj: _IT,
    struct: Union[_ModelT, _ContainsStruct[_IT, _OT], _SupportsPack[_IT]] = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    **kwds,
) -> bytes: ...
@overload
def pack_into(
    obj: _ContainsStruct[_ModelT, _ModelT],
    buffer: _StreamType,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    **kwds,
) -> bytes: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: Union[_SupportsPack[_IT], _ContainsStruct[_IT, _OT]],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    **kwds,
) -> bytes: ...
@overload
def pack_file(
    obj: _ContainsStruct[_ModelT, _ModelT],
    filename: str,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    **kwds,
) -> bytes: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: Union[_SupportsPack[_IT], _ContainsStruct[_IT, _OT]],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    **kwds,
) -> bytes: ...
@overload
def unpack(
    struct: Union[_SupportsUnpack[_OT], _ContainsStruct[_IT, _OT]],
    buffer: bytes | _StreamType,
    /,
    *,
    as_field: bool = ...,
    **kwds,
) -> _OT: ...
@overload
def unpack(
    struct: type[_ModelT],
    buffer: bytes | _StreamType,
    /,
    *,
    as_field: bool = ...,
    **kwds,
) -> _ModelT: ...
def unpack_file(
    struct: Union[_SupportsUnpack[_OT], _ContainsStruct[_IT, _OT]],
    filename: str,
    /,
    *,
    as_field: bool = ...,
    **kwds,
) -> _OT: ...
def sizeof(
    obj: Union[_SupportsSize, _ContainsStruct[Any, Any], _StructLike[Any, Any], type],
    **kwds,
) -> int: ...
