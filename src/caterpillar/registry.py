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
# pyright: reportPrivateUsage=false, reportExplicitAny=false
"""
Module for managing and performing type conversions using custom handlers.

This module provides the :class:`TypeConverter` class, which is designed to
define and manage type conversion handlers for various Python annotations.
These handlers allow you to convert different types (like `int`, `str`, etc.)
into a specialized :class:`_StructLike` object, which could be used in custom
@struct classes.

The :class:`TypeConverter` class allows for both explicit and delegated
conversions, where the user can define how each annotation should be converted,
and even delegate the conversion to external functions.

The module also provides a global registry (:data:`annotation_registry`) to
store type converters and a utility function (:func:`to_struct`) to perform
type conversions using these registered handlers.

Example Usage:
  Define a converter for `int` that converts to `uint16`:

  >>> tc = TypeConverter(int, lambda a, _: Const(a, uint16))

  Alternatively, you can use a decorator to define a type converter:

  >>> @TypeConverter(int)
  ... def int_converter(annotation, kwargs):
  ...     return Const(annotation, uint16)
"""

from typing import Any, Callable
from typing_extensions import override

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

    delegate: Callable[[Any, dict[str, Any]], _StructLike[Any, Any]] | None
    """
    optional delegation function
    """

    def __init__(
        self,
        target: type | None = None,
        delegate: Callable[[Any, dict[str, Any]], _StructLike] | None = None,
    ) -> None:
        self.target: type | None = target
        self.delegate = delegate

    def matches(self, annotation: object) -> bool:
        """Check if this converter matches the given annotation type.

        :param annotation: he type or object to match against the target.
        :type annotation: Any
        :return: True if the annotation matches the target type; otherwise False.
        :rtype: bool
        """
        return False if self.target is None else isinstance(annotation, self.target)

    def convert(self, annotation: object, kwargs: dict[str, Any]) -> _StructLike:
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

    def __call__(
        self, delegate: Callable[[Any, dict[str, Any]], _StructLike]
    ) -> "TypeConverter":
        """Sets the delegate function for this converter and return the instance."""
        self.delegate = delegate
        return self

    @override
    def __repr__(self) -> str:
        """Returns a string representation of the TypeConverter instance."""
        if not self.target:
            return f"<{self.__class__.__name__}>"

        return f"<{self.__class__.__name__} for {self.target.__name__}>"


#: A global registry to store type converters.
annotation_registry: list[TypeConverter] = []


def to_struct(obj: object, **kwargs: Any) -> _StructLike:  # pyright: ignore[reportAny]
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
