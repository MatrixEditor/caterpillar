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
from io import BytesIO
from types import EllipsisType
from typing import Any, Collection, List, Union, Iterable, Callable
from functools import partial

from caterpillar.abc import (
    _ContextLike,
    _StructLike,
    _ContextLambda,
    _Switch,
    getstruct,
)
from caterpillar.byteorder import ByteOrder, byteorder
from caterpillar.options import Flag
from caterpillar.context import CTX_SEQ, CTX_STREAM
from caterpillar._common import unpack_seq, pack_seq, WithoutContextVar

from ._base import Field


class FieldMixin:
    """A simple mixin to support operators used to create :class:`Field` instances."""

    def __or__(self, flag: Flag) -> Field:
        """Creates a field *with* the given flag."""
        return Field(self, byteorder(self)) | flag

    def __xor__(self, flag: Flag) -> Field:
        """Creates a field *without* the given flag."""
        return Field(self, byteorder(self)) ^ flag

    def __matmul__(self, offset: Union[_ContextLambda, int]) -> Field:
        """Creates a field that should start at the given offset."""
        return Field(self, byteorder(self)) @ offset

    def __getitem__(self, dim: Union[_ContextLambda, int, EllipsisType]) -> Field:
        """Returns a sequenced field."""
        return Field(self, byteorder(self))[dim]

    def __rshift__(self, switch: Union[_Switch, dict]) -> Field:
        """Inserts switch options into the new field"""
        return Field(self, byteorder(self)) >> switch

    def __floordiv__(self, condition: Union[_ContextLambda, bool]) -> Field:
        """Returns a field with the given condition"""
        return Field(self, byteorder(self)) // condition

    def __set_byteorder__(self, order: ByteOrder) -> Field:
        """Returns a field with the given byteorder"""
        return Field(self, order=order)

    def __rsub__(self, bits: Union[_ContextLambda, int]) -> Field:
        """Returns a field with the given bit count"""
        return Field(self, byteorder(self), bits=bits)

    def __and__(self, other: _StructLike) -> "Chain":
        """Returns a chain with the next element added at the end"""
        if isinstance(other, Chain):
            return other & self
        return Chain(self, other)


class FieldStruct(FieldMixin):
    """
    A mix-in class combining the behavior of _StructLike with additional
    functionality for packing and unpacking structured data.
    """

    __slots__ = {
        "__byteorder__": (
            """
            An internal field used to measure the byte order of this struct.

            Note that this field will be used during processing only and not during
            parsing or building data. In addition, the actual byte order should be
            retrieved using the :class:`Field` instance within the context.
            """
        ),
        "__bits__": "TBD",
    }

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
        """
        Abstract method to pack a single element.

        :param obj: The element to pack.
        :type obj: Any
        :param context: The current operation context.
        :type context: _ContextLike
        :raises NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def unpack_single(self, context: _ContextLike) -> Any:
        """
        Abstract method to unpack a single element.

        :param context: The current operation context.
        :type context: _ContextLike
        :raises NotImplementedError: This method must be implemented by subclasses.
        :return: The unpacked element.
        """
        raise NotImplementedError

    def pack_seq(self, seq: Collection, context: _ContextLike) -> None:
        """
        Pack a sequence of elements using the provided context.

        :param seq: The sequence of elements to pack.
        :type seq: Iterable
        :param context: The current operation context.
        :type context: _ContextLike
        """
        pack_seq(seq, context, self.pack_single)

    def unpack_seq(self, context: _ContextLike) -> List[Any]:
        """
        Unpack a sequence of elements using the provided context.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: The list of unpacked elements.
        """
        return unpack_seq(context, self.unpack_single)

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        """
        Pack data based on whether the field is sequential or not.

        :param obj: The data to pack.
        :type obj: Any
        :param context: The current operation context.
        :type context: _ContextLike
        """
        (self.pack_single if not context[CTX_SEQ] else self.pack_seq)(obj, context)

    def __unpack__(self, context: _ContextLike) -> Any:
        """
        Unpack data based on whether the field is sequential or not.

        :param context: The current operation context.
        :type context: _ContextLike
        :return: The unpacked data.
        """
        if context[CTX_SEQ]:
            return self.unpack_seq(context)
        return self.unpack_single(context)

    def __repr__(self) -> str:
        """
        String representation of the FieldStruct instance.

        :return: A string representation.
        """
        return f"<{self.__class__.__name__}>"


class Chain(FieldStruct):
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

    __slots__ = ("_elements",)

    def __init__(self, initial: _StructLike, *structs: _StructLike) -> None:
        # start -> next -> next -> next -> done | unpack
        #                                   Y
        # done <- previous <- previous <- start | pack
        self._elements = [getstruct(initial, initial)]
        self._elements += list(map(lambda x: getstruct(x, x), structs))

    @property
    def head(self) -> _StructLike:
        """
        Get the head of the chain, i.e., the first structure.

        :return: The head of the chain.
        :rtype: _StructLike
        """
        return self._elements[0]

    @property
    def tail(self) -> _StructLike:
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

    def __type__(self) -> type:
        """
        Get the type of the tail structure in the chain.

        :return: The type of the tail structure.
        :rtype: type
        """

        return self.tail.__type__()

    def __and__(self, other: _StructLike) -> "Chain":
        """
        Concatenate another structure to the end of the chain.

        :param other: The structure to concatenate.
        :type other: _StructLike
        :return: The updated chain.
        :rtype: Chain
        """
        self._elements.append(getstruct(other, other))
        return self

    def __rand__(self, other: _StructLike) -> "Chain":
        """
        Concatenate another structure to the beginning of the chain.

        :param other: The structure to concatenate.
        :type other: _StructLike
        :return: The updated chain.
        :rtype: Chain
        """
        return self.__and__(other)

    def unpack_single(self, context: _ContextLike) -> memoryview:
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

        return data

    def pack_single(self, obj: Any, context: _ContextLike) -> None:
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


class Operator:
    """Defines a custom opearator (user-defined)

    It operates _infix_ between two statements and takes them as
    agruments. For instance, the following example will return
    an array of structures:

    .. code-block:: python

        from caterpillar.fields import uint16, _infix_
        from caterpillar.model import struct

        M = _infix_(lambda a, b: a[b*2])

        @struct
        class Format:
            f1: uint16 /M/ 3

    This class reserves the `/` operator. It is also possible to
    use this class as a decorator on callable objects:

    .. code-block:: python

        @_infix_
        def M(a, b):
            return a[b*2]

    :param func: The function to be applied.
    :type func: Callable[[Any, Any], _StructLike]
    """

    def __init__(self, func: Callable[[Any, Any], _StructLike]) -> None:
        self.func = func

    def __truediv__(self, arg2) -> _StructLike:
        return self.func(arg2)

    def __rtruediv__(self, arg1) -> "_infix_":
        return Operator(partial(self.func, arg1))

    def __call__(self, arg1, arg2) -> _StructLike:
        return self.func(arg1, arg2)


# utility methods
def get_args(args: Any, context: _ContextLike) -> List[Any]:
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


def get_kwargs(kwargs: dict, context: _ContextLike) -> dict:
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
