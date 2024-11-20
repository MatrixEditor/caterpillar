# Copyright (C) MatrixEditor 2023-2024
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
from typing import Protocol, Union, Callable, Optional

from caterpillar.abc import (
    _ContextLike,
    _StructLike,
    _ContainsStruct,
    getstruct,
    hasstruct,
)
from ._mixin import get_kwargs
from .common import Transformer, Bytes


class _Compressor(Protocol):
    def compress(self, data: bytes, **kwds) -> bytes:
        """Data should get compressed here"""

    def decompress(self, data: bytes, **kwds) -> bytes:
        """Data should get decompressed here"""


class Compressed(Transformer):
    """
    A class representing a compressed transformer.

    :param compressor: The compression algorithm.
    :type compressor: _Compressor
    :param length: The length of the transformer.
    :type length: Union[_ContextLambda, Any]
    """

    def __init__(
        self,
        compressor: _Compressor,
        struct: Union[_ContainsStruct, _StructLike],
        comp_kwargs: Optional[dict] = None,
        decomp_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Initialize a Compressed instance.

        :param compressor: The compression algorithm.
        :type compressor: _Compressor
        :param length: The length of the transformer.
        :type length: Union[_ContextLambda, Any]
        """
        if hasstruct(struct):
            struct = getstruct(struct)
        super().__init__(struct)
        self.compressor = compressor
        self.comp_args = comp_kwargs or {}
        self.decomp_args = decomp_kwargs or {}

    def encode(self, obj: bytes, context: _ContextLike) -> bytes:
        """
        Compress the input data.

        :param obj: The input data to be compressed.
        :type obj: bytes
        :param context: The context information.
        :type context: _ContextLike
        :return: The compressed data.
        :rtype: bytes
        """
        return self.compressor.compress(obj, **get_kwargs(self.comp_args, context))

    def decode(self, parsed: bytes, context: _ContextLike) -> bytes:
        """
        Decompress the input data.

        :param parsed: The compressed data to be decompressed.
        :type parsed: bytes
        :param context: The context information.
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
