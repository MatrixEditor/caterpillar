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
from abc import abstractmethod
from typing import Protocol, Union, Callable, Optional, runtime_checkable

from caterpillar.abc import (
    _ContextLike,
    _StructLike,
    _ContainsStruct,
    getstruct,
    hasstruct,
)
from ._mixin import get_kwargs
from .common import Transformer, Bytes


@runtime_checkable
class _Compressor(Protocol):
    """
    A protocol for compression algorithms, requiring two methods:
    - compress: to compress data
    - decompress: to decompress data

    Any class implementing this protocol must define these methods.
    """

    @abstractmethod
    def compress(self, data: bytes, **kwds) -> bytes:
        """
        Compress the provided data.

        :param data: The data to be compressed.
        :type data: bytes
        :param kwds: Additional keyword arguments specific to the compression method.
        :return: The compressed data.
        :rtype: bytes
        """
        pass

    @abstractmethod
    def decompress(self, data: bytes, **kwds) -> bytes:
        """
        Decompress the provided data.

        :param data: The compressed data to be decompressed.
        :type data: bytes
        :param kwds: Additional keyword arguments specific to the decompression method.
        :return: The decompressed data.
        :rtype: bytes
        """
        pass


class Compressed(Transformer):
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
        struct: Union[_ContainsStruct, _StructLike],
        comp_kwargs: Optional[dict] = None,
        decomp_kwargs: Optional[dict] = None,
    ) -> None:
        if hasstruct(struct):
            struct = getstruct(struct)
        super().__init__(struct)
        self.compressor = compressor
        self.comp_args = comp_kwargs or {}
        self.decomp_args = decomp_kwargs or {}

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


_LengthOrStruct = Union[_ContainsStruct, _StructLike, Callable, int]


def compressed(
    lib: _Compressor,
    obj: _LengthOrStruct,
    comp_kwargs: Optional[dict] = None,
    decomp_kwargs: Optional[dict] = None,
) -> _StructLike:
    if callable(obj) or isinstance(obj, int) or obj is ...:
        obj = Bytes(obj)
    return Compressed(lib, obj, comp_kwargs, decomp_kwargs)


try:
    import zlib

    def ZLibCompressed(
        obj: _LengthOrStruct,
        comp_kwargs: Optional[dict] = None,
        decomp_kwargs: Optional[dict] = None,
    ):
        """
        Create a struct representing zlib compression.
        """
        return compressed(zlib, obj, comp_kwargs, decomp_kwargs)

except ImportError:
    ZLibCompressed = None

try:
    import bz2

    def Bz2Compressed(
        obj: _LengthOrStruct,
        comp_kwargs: Optional[dict] = None,
        decomp_kwargs: Optional[dict] = None,
    ):
        """
        Create a struct representing bz2 compression.
        """
        return compressed(bz2, obj, comp_kwargs, decomp_kwargs)

except ImportError:
    Bz2Compressed = None

try:
    import lzma

    def LZMACompressed(
        obj: _LengthOrStruct,
        comp_kwargs: Optional[dict] = None,
        decomp_kwargs: Optional[dict] = None,
    ):
        """
        Create a struct representing lzma compression.
        """
        return compressed(lzma, obj, comp_kwargs, decomp_kwargs)

except ImportError:
    LZMACompressed = None

try:
    # install package manuall with pip install lzallright
    import lzallright

    def LZOCompressed(
        obj: _LengthOrStruct,
        comp_kwargs: Optional[dict] = None,
        decomp_kwargs: Optional[dict] = None,
    ):
        """
        Create a struct representing LZO compression.
        """
        return compressed(lzallright.LZOCompressor(), obj, comp_kwargs, decomp_kwargs)

except ImportError:
    LZOCompressed = None
