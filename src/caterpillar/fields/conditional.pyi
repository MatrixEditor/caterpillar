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
from caterpillar.abc import _ContextLambda, _ContextLike, _StructLike
from caterpillar.context import ConditionContext
from typing import Any, Dict, List

class ConditionalChain:
    chain: Dict[int, _StructLike]
    conditions: List[_ContextLambda[bool]]
    def __init__(self, struct: _StructLike, condition: _ContextLambda[int]) -> None: ...
    def __type__(self) -> type: ...
    def add(self, struct: _StructLike, func: _ContextLambda[bool]) -> None: ...
    def get_struct(self, context: _ContextLike) -> _StructLike | None: ...
    def __unpack__(self, context: _ContextLike) -> Any: ...
    def __pack__(self, obj: Any, context: _ContextLike) -> None: ...
    def __size__(self, context: _ContextLike) -> int: ...

class If(ConditionContext): ...

class ElseIf(ConditionContext):
    def __enter__(self): ...
    def __exit__(self, *_) -> None: ...

Else: ElseIf
