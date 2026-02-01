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
# pyright: reportPrivateUsage=false, reportAny=false, reportExplicitAny=false
from typing import Any, Protocol, runtime_checkable
from typing_extensions import override

from caterpillar.abc import (
    _ContainsStruct,
    _ContextLike,
    _StructLike,
    _LengthT,
)
from caterpillar.shared import getstruct, hasstruct
from caterpillar.fields._mixin import get_kwargs
from caterpillar.fields.common import Transformer, Bytes


@runtime_checkable
class _Compressor(Protocol):
    """
    A protocol for compression algorithms, requiring two methods:
    - compress: to compress data
    - decompress: to decompress data

    Any class implementing this protocol must define these methods.
    """

    def compress(self, data: bytes, **kwds: Any) -> bytes:
        """
        Compress the provided data.

        :param data: The data to be compressed.
        :type data: bytes
        :param kwds: Additional keyword arguments specific to the compression method.
        :return: The compressed data.
        :rtype: bytes
        """
        ...

    def decompress(self, data: bytes, **kwds: Any) -> bytes:
        """
        Decompress the provided data.

        :param data: The compressed data to be decompressed.
        :type data: bytes
        :param kwds: Additional keyword arguments specific to the decompression method.
        :return: The decompressed data.
        :rtype: bytes
        """
        ...


class Compressed(Transformer[bytes, bytes, bytes, bytes]):
    """
    A transformer class for handling compression and decompression of data.

    This class takes a compression algorithm that implements the `_Compressor` protocol and
    applies it to the data for compression or decompression operations. It allows for
    additional customization through the `comp_kwargs` and `decomp_kwargs` parameters.

    :param compressor: The compression algorithm that implements the _Compressor protocol.
    :type compressor: _Compressor
    :param struct: The struct to be compressed or decompressed, should implement _ContainsStruct or _StructLike.
    :type struct: Union[_ContainsStruct, _StructLike]
    :param comp_kwargs: Optional keyword arguments for the compression method.
    :type comp_kwargs: Optional[dict]
    :param decomp_kwargs: Optional keyword arguments for the decompression method.
    :type decomp_kwargs: Optional[dict]
    """

    def __init__(
        self,
        compressor: _Compressor,
        struct: _StructLike[bytes, bytes] | _ContainsStruct[bytes, bytes],
        comp_kwargs: dict[str, Any] | None = None,
        decomp_kwargs: dict[str, Any] | None = None,
    ) -> None:
        if hasstruct(struct):
            struct = getstruct(struct)
        super().__init__(struct)
        self.compressor: _Compressor = compressor
        self.comp_args: dict[str, Any] = comp_kwargs or {}
        self.decomp_args: dict[str, Any] = decomp_kwargs or {}

    @override
    def encode(self, obj: bytes, context: _ContextLike) -> bytes:
        """
        Compress the input data using the provided compressor.

        :param obj: The data to be compressed.
        :type obj: bytes
        :param context: Context information for compression (e.g., field-specific metadata).
        :type context: _ContextLike
        :return: The compressed data.
        :rtype: bytes
        """
        return self.compressor.compress(obj, **get_kwargs(self.comp_args, context))

    @override
    def decode(self, parsed: bytes, context: _ContextLike) -> bytes:
        """
        Decompress the input data using the provided compressor.

        :param parsed: The compressed data to be decompressed.
        :type parsed: bytes
        :param context: Context information for decompression (e.g., field-specific metadata).
        :type context: _ContextLike
        :return: The decompressed data.
        :rtype: bytes
        """
        return self.compressor.decompress(
            parsed, **get_kwargs(self.decomp_args, context)
        )


_LengthTorStructT = _LengthT | _ContainsStruct[bytes, bytes] | _StructLike[bytes, bytes]


def compressed(
    lib: _Compressor,
    obj: _LengthTorStructT,
    comp_kwargs: dict[str, Any] | None = None,
    decomp_kwargs: dict[str, Any] | None = None,
) -> _StructLike:
    if callable(obj) or isinstance(obj, int) or obj is ...:
        obj = Bytes(obj)
    return Compressed(lib, obj, comp_kwargs, decomp_kwargs)


def ZLibCompressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict[str, Any] | None = None,
    decomp_kwargs: dict[str, Any] | None = None,
):
    """
    Create a struct representing zlib compression.
    """
    try:
        import zlib

        return compressed(zlib, obj, comp_kwargs, decomp_kwargs)
    except ImportError:
        raise NotImplementedError("Could not import zlib!")


def Bz2Compressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict[str, Any] | None = None,
    decomp_kwargs: dict[str, Any] | None = None,
):
    """
    Create a struct representing bz2 compression.
    """
    try:
        import bz2

        return compressed(bz2, obj, comp_kwargs, decomp_kwargs)
    except ImportError:
        raise NotImplementedError("Could not import bz2!")


def LZMACompressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict[str, Any] | None = None,
    decomp_kwargs: dict[str, Any] | None = None,
):
    """
    Create a struct representing lzma compression.
    """
    try:
        import lzma

        return compressed(lzma, obj, comp_kwargs, decomp_kwargs)
    except ImportError:
        raise NotImplementedError("Could not import lzma!")


def LZOCompressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict[str, Any] | None = None,
    decomp_kwargs: dict[str, Any] | None = None,
):
    """
    Create a struct representing LZO compression.
    """
    try:
        # install package manually with pip install lzallright
        import lzallright

        return compressed(lzallright.LZOCompressor(), obj, comp_kwargs, decomp_kwargs)
    except ImportError:
        raise NotImplementedError("Could not import lzallright!")
