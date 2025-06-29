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
from ._base import Field as Field
from .common import Bytes as Bytes, uint32 as uint32
from caterpillar.abc import _ContextLambda, _ContextLike, _StructLike, _ActionLike
from caterpillar.context import CTX_OBJECT as CTX_OBJECT, CTX_STREAM as CTX_STREAM
from caterpillar.exception import (
    StructException as StructException,
    ValidationError as ValidationError,
)
from caterpillar.fields.hook import IOHook as IOHook
from caterpillar.shared import Action as Action
from cryptography.hazmat.primitives import hashes
from typing import Callable, Generic, Optional, Protocol, Self, Type, TypeVar

DEFAULT_DIGEST_PATH: str

class _DigestValue: ...

_AlgoObjT = TypeVar("_AlgoObjT")
_AlgoReturnT = TypeVar("_AlgoReturnT", default=bytes)

class Algorithm(Generic[_AlgoObjT, _AlgoReturnT]):
    name: str
    def __init__(
        self,
        create: _ContextLambda[_AlgoObjT] | None = None,
        update: Callable[[_AlgoObjT, bytes, _ContextLike], _AlgoObjT] | None = None,
        digest: Callable[[_AlgoObjT, _ContextLike], _AlgoReturnT] | None = None,
        name: str | None = None,
    ) -> None: ...
    def create(self, context: _ContextLike) -> _AlgoObjT: ...
    def update(
        self, algo_obj: _AlgoObjT, data: bytes, context: _ContextLike
    ) -> _AlgoObjT: ...
    def digest(self, algo_obj: _AlgoObjT, context: _ContextLike) -> _AlgoReturnT: ...

class Digest(Generic[_AlgoObjT, _AlgoReturnT]):
    algo: Algorithm[_AlgoObjT, _AlgoReturnT]
    name: str
    struct: _StructLike[_AlgoReturnT, _AlgoReturnT]
    path: str
    def __init__(
        self,
        algorithm: Algorithm[_AlgoObjT, _AlgoReturnT],
        struct: _StructLike[_AlgoReturnT, _AlgoReturnT],
        name: str | None = None,
        verify: bool = False,
        path: str | None = None,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *_) -> None: ...
    def begin(self, context: _ContextLike) -> None: ...
    def end_pack(self, context: _ContextLike) -> None: ...
    def end_unpack(self, context: _ContextLike) -> None: ...
    def update(self, data: bytes, context: _ContextLike) -> None: ...
    def verfiy(self, context: _ContextLike) -> None: ...

CTX_DIGEST_OBJ: str
CTX_DIGEST_HOOK: str
CTX_DIGEST_ALGO: str
CTX_DIGEST: str

class DigestFieldAction(Generic[_AlgoObjT, _AlgoReturnT]):
    name: str
    algo: Algorithm[_AlgoObjT, _AlgoReturnT]
    def __init__(
        self, target: str, algorithm: Algorithm[_AlgoObjT, _AlgoReturnT]
    ) -> None: ...
    def update(self, data: bytes, context: _ContextLike) -> None: ...
    def begin(self, context: _ContextLike) -> None: ...
    __action_pack__ = begin
    __action_unpack__ = begin

class DigestField(Generic[_AlgoReturnT], _StructLike[None, _AlgoReturnT]):
    name: str
    struct: _StructLike[_AlgoReturnT, _AlgoReturnT]
    verify: bool
    def __init__(
        self,
        target: str,
        struct: _StructLike[_AlgoReturnT, _AlgoReturnT],
        verify: bool = False,
    ) -> None: ...
    def __type__(self) -> Type[bytes]: ...
    def __size__(self, context: _ContextLike) -> int: ...
    def __pack__(self, obj: None, context: _ContextLike) -> None: ...
    def __unpack__(self, context: _ContextLike) -> _AlgoReturnT: ...
    @staticmethod
    def begin(
        target: str, algo: Algorithm[_AlgoObjT, _AlgoReturnT]
    ) -> DigestFieldAction[_AlgoObjT, _AlgoReturnT]: ...

class _DigestFactory(Protocol[_AlgoReturnT]):
    def __call__(
        self, name: Optional[str] = ..., verify: bool = ..., path: Optional[str] = ...
    ) -> Digest[_AlgoReturnT]: ...

Crc32_Algo: Algorithm[int, int]
Crc32: _DigestFactory[int]
Crc32_Field: DigestField[int]
Adler_Algo: Algorithm[int]
Adler: _DigestFactory[int]
Adler_Field: DigestField[int]
Sha1_Algo: Algorithm[hashes.Hash]
Sha2_224_Algo: Algorithm[hashes.Hash]
Sha2_256_Algo: Algorithm[hashes.Hash]
Sha2_384_Algo: Algorithm[hashes.Hash]
Sha2_512_Algo: Algorithm[hashes.Hash]
Sha3_224_Algo: Algorithm[hashes.Hash]
Sha3_256_Algo: Algorithm[hashes.Hash]
Sha3_384_Algo: Algorithm[hashes.Hash]
Sha3_512_Algo: Algorithm[hashes.Hash]
Md5_Algo: Algorithm[hashes.Hash]
Sha1: _DigestFactory[bytes]
Sha2_224: _DigestFactory[bytes]
Sha2_256: _DigestFactory[bytes]
Sha2_384: _DigestFactory[bytes]
Sha2_512: _DigestFactory[bytes]
Sha3_224: _DigestFactory[bytes]
Sha3_256: _DigestFactory[bytes]
Sha3_384: _DigestFactory[bytes]
Sha3_512: _DigestFactory[bytes]
Md5: _DigestFactory[bytes]

class HMACAlgorithm(Algorithm[hashes.Hash]):
    def __init__(
        self, key: bytes | _ContextLambda[bytes], algorithm: hashes.HashAlgorithm
    ) -> None: ...
    def create(self, context: _ContextLike) -> hashes.Hash: ...
    def update(
        self, algo_obj: hashes.Hash, data: bytes, context: _ContextLike
    ) -> hashes.Hash: ...
    def digest(self, algo_obj: hashes.Hash, context: _ContextLike) -> bytes: ...

class HMAC(Digest[bytes]):
    def __init__(
        self,
        key: bytes | _ContextLambda[bytes],
        algorithm: hashes.HashAlgorithm,
        name: str | None = None,
        verify: bool = False,
        path: str | None = None,
    ) -> None: ...

Sha1_Field: DigestField[bytes]
Sha2_224_Field: DigestField[bytes]
Sha2_256_Field: DigestField[bytes]
Sha2_384_Field: DigestField[bytes]
Sha2_512_Field: DigestField[bytes]
Sha3_224_Field: DigestField[bytes]
Sha3_256_Field: DigestField[bytes]
Sha3_384_Field: DigestField[bytes]
Sha3_512_Field: DigestField[bytes]
Md5_Field: DigestField[bytes]
