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
from caterpillar.abc import _ContextLambda, _StructLike, _ContainsStruct
from typing import Any, Optional, Union

MODE_PACK: int
MODE_UNPACK: int
ATTR_STRUCT: str
ATTR_TYPE: str
ATTR_BYTEORDER: str
ATTR_BITS: str
ATTR_SIGNED: str
ATTR_TEMPLATE: str
ATTR_ACTION_PACK: str
ATTR_ACTION_UNPACK: str

class Action:
    __action_pack__: _ContextLambda
    __action_unpack__: _ContextLambda
    def __init__(
        self,
        pack: _ContextLambda | None = None,
        unpack: _ContextLambda | None = None,
        both: _ContextLambda | None = None,
    ) -> None: ...
    @staticmethod
    def is_action(obj: Any) -> bool: ...

def hasstruct(obj: Any) -> bool: ...
def getstruct(
    obj: Any, /, __default: _StructLike[Any, Any] | None = None
) -> _StructLike[Any, Any] | None: ...
def typeof(struct: _StructLike[Any, Any] | _ContainsStruct[Any, Any]) -> type: ...
