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
from types import NoneType
from typing import Any, Callable, Collection, Generic, Iterable, TypeVar

from caterpillar.abc import _OptionLike

_VT = TypeVar("_VT", default=NoneType)

class Flag(Generic[_VT]):
    name: str
    value: _VT = ...
    _hash_: int
    def __init__(self, name: str, value: _VT = ...) -> None: ...
    def __hash__(self) -> int: ...

GLOBAL_STRUCT_OPTIONS: set[_OptionLike] = ...
GLOBAL_UNION_OPTIONS: set[_OptionLike] = ...
GLOBAL_FIELD_FLAGS: set[_OptionLike] = ...
GLOBAL_BITFIELD_FLAGS: set[_OptionLike] = ...

def configure(base: set[_OptionLike], *flags: _OptionLike) -> None: ...
def set_struct_flags(*flags: _OptionLike, with_union: bool = False) -> None: ...
def set_field_flags(*flags: _OptionLike) -> None: ...
def set_union_flags(*flags: _OptionLike) -> None: ...
def get_flags(obj: Any, attr: str | None = None) -> set[_OptionLike] | None: ...
def has_flag(flag: str | _OptionLike, obj: Any, attr: str | None = None) -> bool: ...
def get_flag(name: str, obj: Any, attr: str | None = None) -> _OptionLike | None: ...

S_DISCARD_UNNAMED: Flag
S_DISCARD_CONST: Flag
S_UNION: Flag
S_REPLACE_TYPES: Flag
S_EVAL_ANNOTATIONS: Flag
S_ADD_BYTES: Flag
S_SLOTS: Flag
F_KEEP_POSITION: Flag
F_DYNAMIC: Flag
F_SEQUENTIAL: Flag
F_OFFSET_OVERRIDE: Flag
O_ARRAY_FACTORY: Flag[Callable[[Iterable], Collection] | None]
B_OVERWRITE_ALIGNMENT: Flag
B_GROUP_END: Flag
B_GROUP_NEW: Flag
B_GROUP_KEEP: Flag
B_NO_AUTO_BOOL: Flag
