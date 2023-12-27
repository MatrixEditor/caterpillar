# Copyright (C) MatrixEditor 2023
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
from __future__ import annotations

import operator

from typing import Callable, Any, Union, Self
from dataclasses import dataclass


from caterpillar.abc import _ContextLambda, _ContextLike


CTX_PARENT = "_parent"
CTX_OBJECT = "_obj"
CTX_OFFSETS = "_offsets"
CTX_STREAM = "_io"
CTX_FIELD = "_field"
CTX_VALUE = "_value"
CTX_POS = "_pos"
CTX_INDEX = "_index"
CTX_PATH = "_path"


class Context(_ContextLike):
    """Represents a context object with attribute-style access."""

    def __setattr__(self, key: str, value) -> None:
        """
        Sets an attribute in the context.

        :param key: The attribute key.
        :param value: The value to be set.
        """
        self[key] = value

    def __getattribute__(self, key: str):
        """
        Retrieves an attribute from the context.

        :param key: The attribute key.
        :return: The value associated with the key.
        """
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if "." not in key:
                try:
                    return self[key]  # Raises an error if the key is not found
                except KeyError:
                    raise AttributeError(key)

            path = key.split(".")
            root = self[path[0]]
            for i in range(1, len(path)):
                root = getattr(root, path[i])

            return root

    @property
    def _root(self) -> _ContextLike:
        current = self
        while CTX_PARENT in current:
            # dict-like access is much faster
            parent = current[CTX_PARENT]
            if parent is None:
                break
            current = parent
        return current


class ExprMixin:
    """
    A mixin class providing methods for creating binary and unary expressions.
    """

    def __add__(self, other) -> ExprMixin:
        return BinaryExpression(operator.add, self, other)

    def __sub__(self, other) -> ExprMixin:
        return BinaryExpression(operator.sub, self, other)

    def __mul__(self, other) -> ExprMixin:
        return BinaryExpression(operator.mul, self, other)

    def __floordiv__(self, other) -> ExprMixin:
        return BinaryExpression(operator.floordiv, self, other)

    def __truediv__(self, other) -> ExprMixin:
        return BinaryExpression(operator.truediv, self, other)

    def __mod__(self, other) -> ExprMixin:
        return BinaryExpression(operator.mod, self, other)

    def __pow__(self, other) -> ExprMixin:
        return BinaryExpression(operator.pow, self, other)

    def __xor__(self, other) -> ExprMixin:
        return BinaryExpression(operator.xor, self, other)

    def __and__(self, other) -> ExprMixin:
        return BinaryExpression(operator.and_, self, other)

    def __or__(self, other) -> ExprMixin:
        return BinaryExpression(operator.or_, self, other)

    def __rshift__(self, other) -> ExprMixin:
        return BinaryExpression(operator.rshift, self, other)

    def __lshift__(self, other) -> ExprMixin:
        return BinaryExpression(operator.lshift, self, other)

    __div__ = __truediv__

    def __radd__(self, other) -> ExprMixin:
        return BinaryExpression(operator.add, other, self)

    def __rsub__(self, other) -> ExprMixin:
        return BinaryExpression(operator.sub, other, self)

    def __rmul__(self, other) -> ExprMixin:
        return BinaryExpression(operator.mul, other, self)

    def __rfloordiv__(self, other) -> ExprMixin:
        return BinaryExpression(operator.floordiv, other, self)

    def __rtruediv__(self, other) -> ExprMixin:
        return BinaryExpression(operator.truediv, other, self)

    def __rmod__(self, other) -> ExprMixin:
        return BinaryExpression(operator.mod, other, self)

    def __rpow__(self, other) -> ExprMixin:
        return BinaryExpression(operator.pow, other, self)

    def __rxor__(self, other) -> ExprMixin:
        return BinaryExpression(operator.xor, other, self)

    def __rand__(self, other) -> ExprMixin:
        return BinaryExpression(operator.and_, other, self)

    def __ror__(self, other) -> ExprMixin:
        return BinaryExpression(operator.or_, other, self)

    def __rrshift__(self, other) -> ExprMixin:
        return BinaryExpression(operator.rshift, other, self)

    def __rlshift__(self, other) -> ExprMixin:
        return BinaryExpression(operator.lshift, other, self)

    def __neg__(self) -> ExprMixin:
        return UnaryExpression("neg", operator.neg, self)

    def __pos__(self) -> ExprMixin:
        return UnaryExpression("pos", operator.pos, self)

    def __invert__(self) -> ExprMixin:
        return UnaryExpression("invert", operator.not_, self)

    def __contains__(self, other) -> ExprMixin:
        return BinaryExpression(operator.contains, self, other)

    def __gt__(self, other) -> ExprMixin:
        return BinaryExpression(operator.gt, self, other)

    def __ge__(self, other) -> ExprMixin:
        return BinaryExpression(operator.ge, self, other)

    def __lt__(self, other) -> ExprMixin:
        return BinaryExpression(operator.lt, self, other)

    def __le__(self, other) -> ExprMixin:
        return BinaryExpression(operator.le, self, other)

    def __eq__(self, other) -> ExprMixin:
        return BinaryExpression(operator.eq, self, other)

    def __ne__(self, other) -> ExprMixin:
        return BinaryExpression(operator.ne, self, other)


@dataclass(frozen=True, repr=False)
class BinaryExpression(ExprMixin, _ContextLambda):
    """
    Represents a binary expression.

    :param operand: The binary operator function.
    :param left: The left operand.
    :param right: The right operand.
    """

    operand: Callable[[Any, Any], Any]
    left: Union[Any, _ContextLambda]
    right: Union[Any, _ContextLambda]

    def __call__(self, context: Context, **kwds):
        lhs = self.left(context, **kwds) if callable(self.left) else self.left
        rhs = self.right(context, **kwds) if callable(self.right) else self.right
        return self.operand(lhs, rhs)

    def __repr__(self) -> str:
        return f"<{self.operand.__name__} left={self.left!r} right={self.right!r}>"


@dataclass(frozen=True)
class UnaryExpression:
    """
    Represents a unary expression.

    :param name: The name of the unary operator.
    :param operand: The unary operator function.
    :param value: The operand.
    """

    name: str
    operand: Callable[[Any], Any]
    value: Union[Any, _ContextLambda]

    def __call__(self, context: Context, **kwds):
        value = self.value(context, **kwds) if callable(self.value) else self.value
        return self.operand(value)

    def __repr__(self) -> str:
        return f"<{self.operand.__name__} value={self.value!r}>"


class ContextPath(ExprMixin, _ContextLambda):
    """
    Represents a lambda function for retrieving a value from a Context based on a specified path.
    """

    def __init__(self, path: str = None) -> None:
        """
        Initializes a ContextPath instance with an optional path.

        :param path: The path to use when retrieving a value from a Context.
        """
        self.path = path
        self._ops_ = []
        self.call_kwargs = None
        self.getitem_args = None

    def __call__(self, context: Context = None, **kwds):
        """
        Calls the lambda function to retrieve a value from a Context.

        :param context: The Context from which to retrieve the value.
        :param kwds: Additional keyword arguments.
        :return: The value retrieved from the Context based on the path.
        """
        if context is None:
            self._ops_.append((operator.call, (), kwds))
            return self
        value = getattr(context, self.path)
        for operation, args, kwargs in self._ops_:
            value = operation(value, *args, **kwargs)
        return value

    def __getitem__(self, key) -> Self:
        self._ops_.append((operator.getitem, (key), {}))
        return self

    def __getattribute__(self, key: str) -> ContextPath:
        """
        Gets an attribute from the ContextPath, creating a new instance if needed.

        :param key: The attribute key.
        :return: A new ContextPath instance with an updated path.
        """
        try:
            return super().__getattribute__(key)
        except AttributeError:
            if not self.path:
                return ContextPath(key)
            return ContextPath(".".join([self.path, key]))

    def __repr__(self) -> str:
        """
        Returns a string representation of the ContextPath.

        :return: A string representation.
        """
        value = f"<Path {self.path!r}"
        if self.call_kwargs is not None:
            value = f"{value}(**{self.call_kwargs})"
        elif self.getitem_args is not None:
            value = f"{value}[{self.getitem_args}]"
        return value + ">"

    def __str__(self) -> str:
        """
        Returns a string representation of the path.

        :return: A string representation of the path.
        """
        return self.path

    @property
    def parent(self) -> ContextPath:
        path = f"{CTX_PARENT}.{CTX_OBJECT}"
        if not self.path:
            return ContextPath(path)
        return ContextPath(".".join([self.path, path]))


class ContextLength(ExprMixin, _ContextLambda):
    def __init__(self, path: ContextPath) -> None:
        self.path = path

    def __call__(self, context: Context = None, **kwds):
        """
        Calls the lambda function to retrieve a value from a Context.

        :param context: The Context from which to retrieve the value.
        :param kwds: Additional keyword arguments (ignored in this implementation).
        :return: The value retrieved from the Context based on the path.
        """
        return len(self.path(context))


this = ContextPath(CTX_OBJECT)
ctx = ContextPath()
parent = ContextPath(".".join([CTX_PARENT, CTX_OBJECT]))
