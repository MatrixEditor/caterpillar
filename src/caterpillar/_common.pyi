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
import types

from typing import Any, Callable, Collection
from caterpillar.abc import _ContextLike, _OT, _IT, _StreamType
from caterpillar.fields._base import Field

class WithoutContextVar:
    context: _ContextLike
    old_value: Any
    value: Any
    name: str
    field: Field
    def __init__(self, context: _ContextLike, name: str, value: Any) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

def unpack_seq(
    context: _ContextLike, unpack_one: Callable[[_ContextLike], _OT]
) -> Collection[_OT]: ...
def pack_seq(
    seq: Collection[_IT],
    context: _ContextLike,
    pack_one: Callable[[_IT, _ContextLike], None],
) -> None: ...
def iseof(stream: _StreamType) -> bool: ...
