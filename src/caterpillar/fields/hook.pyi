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
from typing import Callable, Optional
from typing_extensions import Buffer
from caterpillar.abc import _ContextLike, _ContextLambda
from caterpillar.context import CTX_STREAM as CTX_STREAM
from io import RawIOBase

HookInit = _ContextLambda[None]
HookUpdate = Callable[[bytes, _ContextLike], Optional[bytes]]
HookRead = Callable[[bytes, _ContextLike], Optional[bytes]]
HookWrite = Callable[[bytes, _ContextLike], Optional[bytes]]
HookFinish = _ContextLambda[None]

class IOHook(RawIOBase):
    def __init__(
        self,
        io: RawIOBase | None,
        init: HookInit | None = None,
        update: HookUpdate | None = None,
        read: HookRead | None = None,
        write: HookWrite | None = None,
        finish: HookFinish | None = None,
    ) -> None: ...
    def assert_context_set(self) -> None: ...
    def init(self, context: _ContextLike) -> None: ...
    def finish(self, context: _ContextLike) -> None: ...
    def seekable(self) -> bool: ...
    def readable(self) -> bool: ...
    def read(self, size: int = -1) -> bytes | None: ...
    def write(self, b: Buffer, /) -> int | None: ...
    def writable(self) -> bool: ...
    def tell(self) -> int: ...
    def seek(self, offset: int, whence: int = 0) -> int: ...
