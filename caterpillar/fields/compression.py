# Copyright (C) MatrixEditor 2023
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
from typing import Protocol, Union

from caterpillar.abc import _ContextLike, _StructLike, _ContainsStruct, getstruct
from .common import Transformer


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
        self, compressor: _Compressor, struct: Union[_ContainsStruct, _StructLike]
    ) -> None:
        """
        Initialize a Compressed instance.

        :param compressor: The compression algorithm.
        :type compressor: _Compressor
        :param length: The length of the transformer.
        :type length: Union[_ContextLambda, Any]
        """
        super().__init__(getstruct(struct, struct))
        self.compressor = compressor

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
        return self.compressor.compress(obj)

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
        return self.compressor.decompress(parsed)


try:
    import zlib

    def ZLibCompressed(struct: Union[_ContainsStruct, _StructLike]):
        """
        Create a struct representing zlib compression.
        """
        return Compressed(zlib, struct)

except ImportError:
    ZLibCompressed = None

try:
    import bz2

    def Bz2Compressed(struct: Union[_ContainsStruct, _StructLike]):
        """
        Create a struct representing bz2 compression.
        """
        return Compressed(bz2, struct)

except ImportError:
    Bz2Compressed = None

try:
    import lzma

    def LZMACompressed(struct: Union[_ContainsStruct, _StructLike]):
        """
        Create a struct representing lzma compression.
        """
        return Compressed(lzma, struct)

except ImportError:
    LZMACompressed = None

try:
    # install package manuall with pip install lzallright
    import lzallright

    def LZOCompressed(struct: Union[_ContainsStruct, _StructLike]):
        """
        Create a struct representing LZO compression.
        """
        return Compressed(lzallright.LZOCompressor(), struct)

except ImportError:
    LZOCompressed = None
