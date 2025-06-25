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
from .common import Bytes, Memory
from caterpillar.abc import (
    _ContextLambda,
    _ContextLike,
    _GreedyType,
    _StructLike,
    _LengthT,
)
from caterpillar.context import Context
from cryptography.hazmat.primitives.ciphers import modes, CipherAlgorithm
from cryptography.hazmat.primitives.padding import PaddingContext
from typing import Any, Iterable, Protocol, Type, Union, _VT

class Padding(Protocol):
    def unpadder(self) -> PaddingContext: ...
    def padder(self) -> PaddingContext: ...

KwArgs = Context
_ArgType = Union[_ContextLambda, Any]

class Encrypted(Memory):
    post: _StructLike | None
    def __init__(
        self,
        length: int | _GreedyType | _ContextLambda,
        algorithm: type[CipherAlgorithm],
        mode: Type[modes.Mode] | modes.Mode,
        padding: Padding | type[Padding] | None = None,
        algo_args: Iterable[_ArgType] | None = None,
        mode_args: Iterable[_ArgType] | None = None,
        padding_args: Iterable[_ArgType] | None = None,
        post: _StructLike | None = None,
    ) -> None: ...
    def algorithm(self, context: _ContextLike) -> CipherAlgorithm: ...
    def mode(self, context: _ContextLike) -> modes.Mode: ...
    def padding(self, context: _ContextLike) -> Padding: ...
    def get_instance(
        self,
        type_: Type[_VT],
        field: Any | _VT | None,
        args: Any,
        context: _ContextLambda,
    ) -> _VT: ...
    def pack_single(self, obj: Any, context: _ContextLike) -> None: ...
    def unpack_single(self, context: _ContextLike) -> memoryview: ...

_KeyType = Union[int, str, bytes, _ContextLambda[Union[int, str, bytes]]]

class KeyCipher(Bytes):
    key: _KeyType
    key_length: int
    is_lazy: bool
    def __init__(self, key: _KeyType, length: _LengthT | None = None) -> None: ...
    def set_key(self, key: _KeyType, context: _ContextLike | None = None) -> None: ...
    def process(self, obj: bytes, context: _ContextLike) -> bytes: ...
    def pack_single(self, obj: bytes, context: _ContextLike) -> None: ...
    def unpack_single(self, context: _ContextLike) -> bytes: ...

class Xor(KeyCipher): ...
class Or(KeyCipher): ...
class And(KeyCipher): ...
