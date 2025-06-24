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
