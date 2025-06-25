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
from .common import Transformer
from caterpillar.abc import (
    _ContainsStruct,
    _ContextLike,
    _StructLike,
    _LengthT,
)
from typing import Protocol, runtime_checkable

@runtime_checkable
class _Compressor(Protocol):
    def compress(self, data: bytes, **kwds) -> bytes: ...
    def decompress(self, data: bytes, **kwds) -> bytes: ...

class Compressed(Transformer[bytes, bytes, bytes, bytes]):
    compressor: _Compressor
    comp_args: dict
    decomp_args: dict
    def __init__(
        self,
        compressor: _Compressor,
        struct: _ContainsStruct[bytes, bytes] | _StructLike[bytes, bytes],
        comp_kwargs: dict | None = None,
        decomp_kwargs: dict | None = None,
    ) -> None: ...
    def encode(self, obj: bytes, context: _ContextLike) -> bytes: ...
    def decode(self, parsed: bytes, context: _ContextLike) -> bytes: ...

_LengthTorStructT = _LengthT | _ContainsStruct[bytes, bytes] | _StructLike[bytes, bytes]

def compressed(
    lib: _Compressor,
    obj: _LengthTorStructT,
    comp_kwargs: dict | None = None,
    decomp_kwargs: dict | None = None,
) -> _StructLike[bytes, bytes]: ...

def ZLibCompressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict | None = None,
    decomp_kwargs: dict | None = None,
) -> _StructLike[bytes, bytes]: ...
def Bz2Compressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict | None = None,
    decomp_kwargs: dict | None = None,
) -> _StructLike[bytes, bytes]: ...
def LZMACompressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict | None = None,
    decomp_kwargs: dict | None = None,
) -> _StructLike[bytes, bytes]: ...
def LZOCompressed(
    obj: _LengthTorStructT,
    comp_kwargs: dict | None = None,
    decomp_kwargs: dict | None = None,
) -> _StructLike[bytes, bytes]: ...
