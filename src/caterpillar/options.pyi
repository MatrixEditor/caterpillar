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

_VT = TypeVar("_VT", default=NoneType)

class Flag(Generic[_VT]):
    name: str
    value: _VT | None = ...
    _hash_: int
    def __init__(self, name: str, value: _VT | None = None) -> None: ...
    def __hash__(self) -> int: ...

GLOBAL_STRUCT_OPTIONS: set[Flag] = ...
GLOBAL_UNION_OPTIONS: set[Flag] = ...
GLOBAL_FIELD_FLAGS: set[Flag] = ...
GLOBAL_BITFIELD_FLAGS: set[Flag] = ...

def configure(base: set[Flag], *flags: Flag) -> None: ...
def set_struct_flags(*flags: Flag, with_union: bool = False) -> None: ...
def set_field_flags(*flags: Flag) -> None: ...
def set_union_flags(*flags: Flag) -> None: ...
def get_flags(obj: Any, attr: str | None = None) -> set[Flag] | None: ...
def has_flag(flag: str | Flag, obj: Any, attr: str | None = None) -> bool: ...
def get_flag(name: str, obj: Any, attr: str | None = None) -> Flag | None: ...

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
O_ARRAY_FACTORY: Flag[Callable[[Iterable], Collection]]
B_OVERWRITE_ALIGNMENT: Flag
B_GROUP_END: Flag
B_GROUP_NEW: Flag
B_GROUP_KEEP: Flag
B_NO_AUTO_BOOL: Flag