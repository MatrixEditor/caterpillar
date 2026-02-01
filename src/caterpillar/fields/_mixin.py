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
# pyright: reportPrivateUsage=false, reportExplicitAny=false
from io import BytesIO
from collections.abc import Collection, Iterable
from functools import partial
from typing import Any, Callable, Generic
from typing_extensions import Self, override

from caterpillar.byteorder import byteorder
from caterpillar.options import Flag
from caterpillar.context import CTX_SEQ, CTX_STREAM
from caterpillar._common import unpack_seq, pack_seq, WithoutContextVar
from caterpillar.shared import getstruct

from ._base import Field
from caterpillar.abc import (
    _ContextLambda,
    _ContextLike,
    _StructLike,
    _LengthT,
    _IT,
    _OT,
    _OptionLike,
    _EndianLike,
    _SwitchLambda,
    _ArgType,
    _ContainsStruct
)


class ByteOrderMixin(Generic[_IT, _OT]):
    def __set_byteorder__(self, order: _EndianLike) -> Field[_IT, _OT]:
        """Returns a field with the given byteorder"""
        return Field(self, order=order)  # pyright: ignore[reportArgumentType]


class FieldMixin(ByteOrderMixin[_IT, _OT]):
    """A simple mixin to support operators used to create :class:`Field` instances."""

    def __or__(self, flag: _OptionLike) -> Field[_IT, _OT]:
        """Creates a field *with* the given flag."""
        # fmt: off
        return Field(self, byteorder(self)) | flag # pyright: ignore[reportArgumentType]

    def __xor__(self, flag: Flag) -> Field[_IT, _OT]:
        """Creates a field *without* the given flag."""
        # fmt: off
        return Field(self, byteorder(self)) ^ flag # pyright: ignore[reportArgumentType]

    def __matmul__(self, offset: _ContextLambda[int] | int) -> Field[_IT, _OT]:
        """Creates a field that should start at the given offset."""
        # fmt: off
        return Field(self, byteorder(self)) @ offset # pyright: ignore[reportArgumentType]

    def __getitem__(self, dim: _LengthT) -> Field[Collection[_IT], Collection[_OT]]:
        """Returns a sequenced field."""
        # fmt: off
        return Field(self, byteorder(self))[dim] # pyright: ignore[reportArgumentType]

    def __rshift__(
        self, switch: _SwitchLambda | dict[str, _StructLike]
    ) -> Field[_IT, _OT]:
        """Inserts switch options into the new field"""
        # fmt: off
        return Field(self, byteorder(self)) >> switch # pyright: ignore[reportArgumentType]

    def __floordiv__(self, condition: _ContextLambda[bool] | bool) -> Field[_IT, _OT]:
        """Returns a field with the given condition"""
        # fmt: off
        return Field(self, byteorder(self)) // condition # pyright: ignore[reportArgumentType]

    def __rsub__(self, bits: _ContextLambda[int] | int) -> Field[_IT, _OT]:
        """Returns a field with the given bit count"""
        # fmt: off
        return Field(self, byteorder(self), bits=bits) # pyright: ignore[reportArgumentType]

    def __and__(self, other: "Chain | _StructLike") -> "Chain":
        """Returns a chain with the next element added at the end"""
        # fmt: off
        if isinstance(other, Chain):
            return other & self  # pyright: ignore[reportOperatorIssue, reportUnknownVariableType]
        return Chain(self, other)  # pyright: ignore[reportArgumentType]


class FieldStruct(FieldMixin[_IT, _OT]):
    """
    A mix-in class combining the behavior of _StructLike with additional
    functionality for packing and unpacking structured data.
    """

    #!! Removed in 2.8.0
    # __slots__: tuple[str, ...] = ("__byteorder__", "__bits__")
    # __byteorder__: _EndianLike | None
    # __bits__: int | _ContextLambda[int] | None

    def pack_single(self, obj: _IT, context: _ContextLike) -> None:
        """
        Abstract method to pack a single element.

        :param obj: The element to pack.
        :type obj: Any
        :param context: The current operation context.
        :type context: _ContextLike
        :raises NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def unpack_single(self, context: _ContextLike) -> _OT:
        """
        Abstract method to unpack a single element.

        :param context: The current operation context.
        :type context: _ContextLike
        :raises NotImplementedError: This method must be implemented by subclasses.
        :return: The unpacked element.
        """
        raise NotImplementedError

    def pack_seq(self, seq: Collection[_IT], context: _ContextLike) -> None:
        """
        Pack a sequence of elements using the provided context.

        :param seq: The sequence of elements to pack.
        :type seq: Iterable
        :param context: The current operation context.
        :type context: _ContextLike
        """
        pack_seq(seq, context, self.pack_single)

    def unpack_seq(self, context: _ContextLike) -> Collection[_OT]:
        """
        Unpack a sequence of elements using the provided context.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: The list of unpacked elements.
        """
        return unpack_seq(context, self.unpack_single)

    def __pack__(self, obj: _IT, context: _ContextLike) -> None:
        """
        Pack data based on whether the field is sequential or not.

        :param obj: The data to pack.
        :type obj: Any
        :param context: The current operation context.
        :type context: _ContextLike
        """
        # fmt: off
        (self.pack_single if not context[CTX_SEQ] else self.pack_seq)(obj, context)  # pyright: ignore[reportArgumentType]

    def __unpack__(self, context: _ContextLike) -> _OT:
        """
        Unpack data based on whether the field is sequential or not.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: The unpacked data.
        """
        # fmt: off
        return (self.unpack_seq if context[CTX_SEQ] else self.unpack_single)(context)  # pyright: ignore[reportReturnType]

    @override
    def __repr__(self) -> str:
        """
        String representation of the FieldStruct instance.

        :return: A string representation.
        """
        return f"<{self.__class__.__name__}>"


class Chain(FieldStruct[_IT, _OT]):
    """
    Represents a chain of structures where each structure in the chain is linked
    to the next one, forming a sequence.

    :param initial: The initial structure in the chain.
    :param structs: Additional structures to be added to the chain.

    The chain allows packing and unpacking data through its elements in sequence.

    .. note::
        - Unpacking travels from the head to the tail.
        - Packing travels from the tail to the head.
    """

    __slots__: tuple[str, ...] = ("_elements",)

    def __init__(
        self,
        initial: _StructLike[_IT, bytes],
        *structs: _StructLike[bytes, bytes],
        tail: _StructLike[bytes, _OT] | None = None,
    ) -> None:
        # fmt: off
        # start -> next -> next -> next -> done | unpack
        #                                   Y
        # done <- previous <- previous <- start | pack
        self._elements: list[_StructLike] = [getstruct(initial) or initial]  # pyright: ignore[reportAttributeAccessIssue]
        self._elements += [x for x in map(lambda x: getstruct(x, x), structs) if x]  # pyright: ignore[reportAttributeAccessIssue]
        if tail:
            self._elements.append(tail)

    @property
    def head(self) -> _StructLike[_IT, bytes]:
        """
        Get the head of the chain, i.e., the first structure.

        :return: The head of the chain.
        :rtype: _StructLike
        """
        return self._elements[0]

    @property
    def tail(self) -> _StructLike[bytes, _OT]:
        """
        Get the tail of the chain, i.e., the last structure.

        :return: The tail of the chain.
        :rtype: _StructLike
        """

        return self._elements[-1]

    def __size__(self, context: _ContextLike) -> int:
        """
        Calculate the size of the chain in bytes.

        :param context: The context for the calculation.
        :type context: _ContextLike
        :return: The size of the chain.
        :rtype: int
        """
        return self.head.__size__(context)

    def __type__(self) -> type | str | None:
        """
        Get the type of the tail structure in the chain.

        :return: The type of the tail structure.
        :rtype: type
        """
        return self.tail.__type__()

    @override
    def __and__(self, other: "Chain | _StructLike | _ContainsStruct") -> Self:
        """
        Concatenate another structure to the end of the chain.

        :param other: The structure to concatenate.
        :type other: _StructLike
        :return: The updated chain.
        :rtype: Chain
        """
        self._elements.append(getstruct(other) or other)
        return self

    def __rand__(self, other: "Chain") -> Self:
        """
        Concatenate another structure to the beginning of the chain.

        :param other: The structure to concatenate.
        :type other: _StructLike
        :return: The updated chain.
        :rtype: Chain
        """
        return self.__and__(other)

    @override
    def unpack_single(self, context: _ContextLike) -> _OT:
        """
        Unpack a single data instance from the chain.

        :param context: The context for the unpacking operation.
        :type context: _ContextLike
        :return: A memory view representing the unpacked data.
        :rtype: memoryview
        """
        data = None
        for i, struct in enumerate(self._elements):
            stream = BytesIO(data) if i != 0 else context[CTX_STREAM]
            with (
                WithoutContextVar(context, CTX_STREAM, stream),
                WithoutContextVar(context, CTX_SEQ, False),
            ):
                data = struct.__unpack__(context)

        return data  # pyright: ignore[reportReturnType]

    @override
    def pack_single(self, obj: _IT, context: _ContextLike) -> None:
        """
        Pack a single data instance into the chain.

        :param Any obj: The data to pack into the chain.
        :param context: The context for the packing operation.
        :type context: _ContextLike
        """
        count = len(self._elements)
        for i, struct in enumerate(reversed(self._elements)):
            if i == count - 1:
                # Last struct, use the provided context stream directly
                struct.__pack__(obj, context)
            else:
                # Not the last struct, use a temporary BytesIO object
                with (
                    BytesIO() as stream,
                    WithoutContextVar(context, CTX_STREAM, stream),
                    WithoutContextVar(context, CTX_SEQ, False),
                ):
                    struct.__pack__(obj, context)
                    obj = stream.getvalue()


class Operator(Generic[_IT, _OT]):
    """Defines a custom opearator (user-defined)

    It operates _infix_ between two statements and takes them as
    agruments. For instance, the following example will return
    an array of structures:

    .. code-block:: python

        from caterpillar.fields import uint16, Operator
        from caterpillar.model import struct

        M = Operator(lambda a, b: a[b*2])

        @struct
        class Format:
            f1: uint16 /M/ 3

    This class reserves the `/` operator. It is also possible to
    use this class as a decorator on callable objects:

    .. code-block:: python

        @Operator
        def M(a, b):
            return a[b*2]

    :param func: The function to be applied.
    :type func: Callable[[Any, Any], _StructLike]
    """

    def __init__(self, func: Callable[[Any, Any], _StructLike[_IT, _OT]]) -> None:
        self.func: Callable[[Any, Any], _StructLike[_IT, _OT]] = func

    def __truediv__(self, arg2: object) -> _StructLike[_IT, _OT]:
        return self.func(arg2)  # pyright: ignore[reportCallIssue]

    def __rtruediv__(self, arg1: object) -> "Operator[_IT, _OT]":
        return Operator(partial(self.func, arg1))

    def __call__(self, arg1: object, arg2: object) -> _StructLike[_IT, _OT]:
        return self.func(arg1, arg2)


# utility methods
def get_args(
    args: _ArgType | list[_ArgType],
    context: _ContextLike,
) -> list[Any]:
    """
    Get arguments for an instance.

    :param args: Input arguments.
    :type args: Any
    :param context: The current operation context.
    :type context: _ContextLike
    :return: A list of processed arguments.
    :rtype: list
    """
    args = list(args) if isinstance(args, Iterable) else [args]
    for i, argument in enumerate(args):
        if callable(argument):
            args[i] = argument(context)
    return args


def get_kwargs(kwargs: dict[str, _ArgType], context: _ContextLike) -> dict[str, Any]:
    """
    Process a dictionary of keyword arguments, replacing callable values with their
    results.

    :param kwargs: Dictionary of keyword arguments.
    :type kwargs: dict
    :param context: The current operation context.
    :type context: _ContextLike
    :return: A new dictionary with processed keyword arguments.
    :rtype: dict
    """
    for key, value in kwargs.items():
        if callable(value):
            kwargs[key] = value(context)
    return kwargs
