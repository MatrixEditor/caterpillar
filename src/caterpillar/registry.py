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

from typing import Any

from caterpillar.abc import _StructLike
from caterpillar.exception import ValidationError


class TypeConverter:
    """
    A utility class to define and manage type conversion handlers for annotations.

    Type converters take the placed annotation and convert it into
    a :code:`_StructLike` object. For instance, a simple converter that
    always returns :code:`uint32` for an object of the Python `int` class might look
    like this:

    >>> tc = TypeConverter(int, lambda a, _: Const(a, uint16))

    or directly as annotation

    >>> @TypeConverter(int)
    ... def int_converter(annotation, kwargs):
    ...     return Const(annotation, uint16)
    ...

    :param target: the target type, defaults to None
    :type target: Type, optional
    :param delegate: optional delegation function, defaults to None
    :type delegate: Callable[[Any, dict], _StructLike], optional
    """

    def __init__(self, target=None, delegate=None) -> None:
        self.target = target
        self.delegate = delegate

    def matches(self, annotation: Any) -> bool:
        """Check if this converter matches the given annotation type.

        :param annotation: he type or object to match against the target.
        :type annotation: Any
        :return: True if the annotation matches the target type; otherwise False.
        :rtype: bool
        """
        return False if self.target is None else isinstance(annotation, self.target)

    def convert(self, annotation: Any, kwargs: dict) -> _StructLike:
        """Convert the given annotation (uses the delegate function by default).

        :param annotation: The object to be converted.
        :type annotation: Any
        :param kwargs: Additional arguments for the conversion.
        :type kwargs: dict
        :raises NotImplementedError: If no delegate is defined for the converter.
        :return: The converted object.
        :rtype: _StructLike
        """
        if self.delegate is None:
            raise NotImplementedError("NOT IMPLEMENTED")

        return self.delegate(annotation, kwargs)

    def __call__(self, delegate) -> Any:
        """Sets the delegate function for this converter and return the instance."""
        self.delegate = delegate
        return self

    def __repr__(self) -> str:
        """Returns a string representation of the TypeConverter instance."""
        if not self.target:
            return f"<{self.__class__.__name__}>"

        return f"<{self.__class__.__name__} for {self.target.__name__}>"


# A global registry to store type converters.
annotation_registry: list[TypeConverter] = []


def to_struct(obj: Any, **kwargs) -> _StructLike:
    """Convert an object to a :code:`_StruckLike` object using registered type converters.

    This function will not convert any objects that are already
    implementing the functions of :code:`_StructLike`.

    :param obj: The object to be converted.
    :type obj: Any
    :param kwargs: Additional arguments passed to the conversion handler.
    :raises ValidationError: If no matching type converter is found for the object.
    :return: the converted object
    :rtype: _StructLike
    """

    # If the object is already a structured-like instance, return it.
    if isinstance(obj, _StructLike):
        return obj

    global annotation_registry

    # Find and use only the first registered converter that matches the object's type.
    handler = next(filter(lambda x: x.matches(obj), annotation_registry), None)
    if handler is None:
        msg = (
            f"The object of type '{obj.__class__}' could not be converted to a struct, because "
            "the placed annotation does not have a corresponding handler:\n "
            f"type: {type(obj)},\n annotation: {obj!r}"
        )
        raise ValidationError(msg)

    return handler.convert(obj, kwargs)
