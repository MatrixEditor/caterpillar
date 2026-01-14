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

from typing import Any, Final, Generic, TypeVar
from typing_extensions import override

from caterpillar.byteorder import Arch
from caterpillar.exception import DelegationError, StructException
from caterpillar.context import CTX_STREAM, CTX_FIELD, CTX_ARCH, CTX_SEQ
from caterpillar.options import Flag
from caterpillar._common import WithoutContextVar
from caterpillar.shared import getstruct
from caterpillar.abc import _ContextLambda, _ContextLike, _StructLike, _StreamType, _IT

from ._mixin import FieldStruct
from .common import uint16, uint24, uint32, uint64, uint8
from .common import int16, int32, int64, int24, int8
from .common import UInt, Int

_PtrValueT = TypeVar("_PtrValueT")


PTR_STRICT: Flag[None] = Flag("pointer.strict-mode")


class pointer(Generic[_PtrValueT], int):
    """
    A custom integer subclass representing a pointer to another struct within the stream.

    :ivar Any obj: The associated object, if any.
    """

    obj: _PtrValueT | None  # pyright: ignore[reportUninitializedInstanceVariable]

    @override
    def __repr__(self) -> str:
        result = super().__repr__()
        if self.obj is not None:
            result = f"<{type(self.obj).__name__}* {hex(self)}>"
        return result

    def get(self):
        return self.obj


class Pointer(FieldStruct[int, pointer[_PtrValueT]]):
    """
    A struct that represents a pointer to another struct within the stream.

    :ivar model: An optional configurable model to parse at the offset position.
    :ivar struct: The configured struct to use.
    """

    __slots__: tuple[str, ...] = ("model", "struct")

    def __init__(
        self,
        struct: _StructLike[int, int] | _ContextLambda[_StructLike[int, int]],
        model: _StructLike[_PtrValueT, _PtrValueT] | None = None,
    ) -> None:
        self.struct: _StructLike[int, int] | _ContextLambda[_StructLike[int, int]] = (
            struct
        )
        self.model: _StructLike[_PtrValueT, _PtrValueT] | None = (
            getstruct(model, model) if model is not None else None
        )

    def __mul__(self, model: _StructLike[_IT, _IT]) -> "Pointer[_IT]":
        """
        Create a new Pointer with a specified model.

        :param model: The model to use.
        :return: A new Pointer with the specified model.
        :rtype: Pointer
        """
        return self.__class__(self.struct, model)  # pyright: ignore[reportReturnType]

    def __type__(self):
        """
        Get the type associated with the Pointer.

        :return: The type associated with the Pointer.
        :rtype: type
        """
        return pointer

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the Pointer struct.

        :param context: The context for size calculation.
        :return: The size of the Pointer struct.
        :rtype: int
        """
        struct = self.struct
        if callable(self.struct):
            struct = self.struct(context)
        return struct.__size__(context)

    @override
    def unpack_single(self, context: _ContextLike) -> pointer[_PtrValueT]:
        """
        Unpack a single value using the Pointer struct.

        :param context: The context for unpacking.
        :return: The unpacked value.
        """
        # fmt: off
        struct = self.struct
        if callable(struct):
            struct = self.struct(context)  # pyright: ignore[reportCallIssue]

        stream: _StreamType = context[CTX_STREAM]  # pyright: ignore[reportAny]
        start = stream.tell()
        with WithoutContextVar(context, CTX_SEQ, False):
            value: int = struct.__unpack__(context)
            # cleanup before further parsing
            value: int = self._clean(value, context)

            if self.model is None:
                return self._create(value, start, None, context)

            offset: int = self._to_offset(value, start, context)
            model_obj = None
            if offset != 0:
                # using an if-statement here reduces time overhead
                # of this branch
                fallback: int = stream.tell()
                try:
                    stream.seek(offset)
                    model_obj = self.model.__unpack__(context)
                except StructException as exc:
                    if context[CTX_FIELD].has_flag(PTR_STRICT):
                        raise DelegationError(
                            "Could not parse model!", context
                        ) from exc
                stream.seek(fallback)
        return self._create(value, start, model_obj, context)

    @override
    def pack_single(self, obj: int, context: _ContextLike) -> None:
        """
        Pack a single value using the Pointer struct.

        :param obj: The value to pack.
        :param context: The context for packing.
        """
        # fmt: off
        struct = self.struct
        if callable(struct):
            struct = self.struct(context)  # pyright: ignore[reportCallIssue]

        with WithoutContextVar(context, CTX_SEQ, False):
            struct.__pack__(int(obj), context)

    def _to_offset(self, value: int, start: int, context: _ContextLike) -> int:
        """
        Convert the pointer value to an offset.

        :param value: The pointer value.
        :param start: The starting position in the stream.
        :param context: The context for the conversion.
        :return: The offset value.
        :rtype: int
        """
        return value

    def _clean(self, value: int, context: _ContextLike) -> int:
        """
        Clean the pointer value.

        :param value: The pointer value.
        :param context: The context for cleaning.
        :return: The cleaned pointer value.
        """
        return value

    def _create(
        self,
        value: int,
        start: int,
        model_obj: _PtrValueT | None,
        context: _ContextLike,
    ) -> pointer[_PtrValueT]:
        """
        Create a new pointer object.

        :param value: The pointer value.
        :param start: The starting position in the stream.
        :param model_obj: The object parsed from the model.
        :param context: The context for creation.
        :return: The created pointer object.
        """
        ptr: pointer[_PtrValueT] = pointer(value)
        setattr(ptr, "obj", model_obj)
        return ptr


UNSIGNED_POINTER_TYS: dict[int, _StructLike[int, int]] = {
    x.__bits__: x for x in [uint8, uint16, uint24, uint32, uint64]
}
SIGNED_POINTER_TYS: dict[int, _StructLike[int, int]] = {
    x.__bits__: x for x in [int8, int16, int24, int32, int64]
}


def uintptr_fn(context: _ContextLike) -> _StructLike[int, int]:
    """
    Generator function to decide which struct to use as the pointer type based
    on the current architecture.

    :param _ContextLike context: The input context.
    :return: The struct to use.
    :rtype: _StructLike
    """
    arch: Arch = context._root.get(CTX_ARCH, context[CTX_FIELD].arch)
    return UNSIGNED_POINTER_TYS.get(arch.ptr_size, UInt(arch.ptr_size))


def intptr_fn(context: _ContextLike) -> _StructLike[int, int]:
    """
    Generator function to decide which struct to use as the pointer type based
    on the current architecture.

    :param _ContextLike context: The input context.
    :return: The struct to use.
    :rtype: _StructLike
    """
    arch: Arch = context._root.get(CTX_ARCH, context[CTX_FIELD].arch)
    return SIGNED_POINTER_TYS.get(arch.ptr_size, Int(arch.ptr_size))


uintptr: Final[Pointer[Any]] = Pointer(uintptr_fn)
intptr: Final[Pointer[Any]] = Pointer(intptr_fn)


class relative_pointer(pointer[_PtrValueT]):
    """
    A custom integer subclass representing a relative pointer to another struct within the stream.

    :ivar obj: The associated object, if any.
    :ivar base: The base offset.
    :ivar absolute: The absolute offset.
    """

    base: int  # pyright: ignore[reportUninitializedInstanceVariable]

    @property
    def absolute(self) -> int:
        """
        Get the absolute offset.

        :return: The absolute offset.
        :rtype: int
        """
        return self + self.base


class RelativePointer(Pointer[_PtrValueT]):
    """
    A struct that represents a relative pointer to another struct within the stream.
    """

    @override
    def __type__(self):
        """
        Get the type associated with the RelativePointer.

        :return: The type associated with the RelativePointer.
        :rtype: type
        """
        if self.model is not None:
            return f"relative_pointer[{self.model.__type__().__name__}]"

        return relative_pointer

    @override
    def _to_offset(self, value: int, start: int, context: _ContextLike) -> int:
        """
        Convert the relative pointer value to an offset.

        :param value: The relative pointer value.
        :param start: The starting position in the stream.
        :param context: The context for the conversion.
        :return: The offset value.
        :rtype: int
        """
        return start + value

    @override
    def _create(
        self,
        value: int,
        start: int,
        model_obj: _PtrValueT | None,
        context: _ContextLike,
    ) -> pointer[_PtrValueT]:
        """
        Create a new relative pointer object.

        :param value: The relative pointer value.
        :param start: The starting position in the stream.
        :param model_obj: The object parsed from the model.
        :param context: The context for creation.
        :return: The created relative pointer object.
        """
        ptr = super()._create(value, start, model_obj, context)
        setattr(ptr, "base", start)
        return ptr


offintptr: Final[RelativePointer[Any]] = RelativePointer(intptr_fn)
offuintptr: Final[RelativePointer[Any]] = RelativePointer(uintptr_fn)