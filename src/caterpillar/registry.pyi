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
from caterpillar.abc import _StructLike
from typing import Any, Callable, Self

class TypeConverter:
    target: type
    delegate: Callable[[Any, dict], _StructLike]
    def __init__(
        self,
        target: type | None = None,
        delegate: Callable[[Any, dict], _StructLike] | None = None,
    ) -> None: ...
    def matches(self, annotation: Any) -> bool: ...
    def convert(self, annotation: Any, kwargs: dict) -> _StructLike: ...
    def __call__(self, delegate: Callable[[Any, dict], _StructLike]) -> Self: ...

annotation_registry: list[TypeConverter]

def to_struct(obj: Any, **kwargs) -> _StructLike: ...
