from typing import Callable, Iterable, Type, TypeVar, overload
from caterpillar._C import *  # noqa
from caterpillar._C import __all__ as _c_all
from caterpillar import native_support

_T = TypeVar("_T")

if native_support():
    @overload
    def struct(
        cls: None = None,
        /,
        options: Iterable[Option] = ...,
        endian: Endian = ...,
        arch: Arch = ...,
        field_options: Iterable[Option] = ...,
    ) -> Callable[[Type[_T]], Type[_T]]: ...
    @overload
    def struct(
        cls: Type[_T],
        /,
        options: Iterable[Option] = ...,
        endian: Endian = ...,
        arch: Arch = ...,
        field_options: Iterable[Option] = ...,
    ) -> Type[_T]: ...

    __all__ = _c_all + ["struct"]  # pyright: ignore[reportUnsupportedDunderAll]
