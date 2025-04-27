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
from __future__ import annotations

import operator
import sys
import warnings

from typing import Callable, Any, Union, Self
from types import FrameType
from dataclasses import dataclass


from caterpillar.abc import _ContextLambda, _ContextLike
from caterpillar.exception import StructException
from caterpillar.registry import to_struct

CTX_PARENT = "_parent"
CTX_OBJECT = "_obj"
CTX_OFFSETS = "_offsets"
CTX_STREAM = "_io"
CTX_FIELD = "_field"
CTX_VALUE = "_value"
CTX_POS = "_pos"
CTX_INDEX = "_index"
CTX_PATH = "_path"
CTX_SEQ = "_is_seq"
CTX_ARCH = "_arch"


class Context(dict):
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
            return self.__context_getattr__(key)

    def __context_getattr__(self, path: str):
        """
        Retrieves an attribute from the context.

        :param key: The attribute key.
        :return: The value associated with the key.
        """
        nodes = path.split(".")
        obj = (
            self[nodes[0]]
            if nodes[0] in self
            else object.__getattribute__(self, nodes[0])
        )

        for i in range(1, len(nodes)):
            obj = getattr(obj, nodes[i])

        return obj

    def __context_setattr__(self, path: str, value: Any) -> None:
        nodes = path.rsplit(".", 1)
        if len(nodes) == 1:
            self[path] = value
        else:
            obj = self.__context_getattr__(nodes[0])
            setattr(obj, nodes[1], value)

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

    def __add__(self, other):
        return BinaryExpression(operator.add, self, other)

    def __sub__(self, other):
        return BinaryExpression(operator.sub, self, other)

    def __mul__(self, other):
        return BinaryExpression(operator.mul, self, other)

    def __floordiv__(self, other):
        return BinaryExpression(operator.floordiv, self, other)

    def __truediv__(self, other):
        return BinaryExpression(operator.truediv, self, other)

    def __mod__(self, other):
        return BinaryExpression(operator.mod, self, other)

    def __pow__(self, other):
        return BinaryExpression(operator.pow, self, other)

    def __xor__(self, other):
        return BinaryExpression(operator.xor, self, other)

    def __and__(self, other):
        return BinaryExpression(operator.and_, self, other)

    def __or__(self, other):
        return BinaryExpression(operator.or_, self, other)

    def __rshift__(self, other):
        return BinaryExpression(operator.rshift, self, other)

    def __lshift__(self, other):
        return BinaryExpression(operator.lshift, self, other)

    __div__ = __truediv__

    def __radd__(self, other):
        return BinaryExpression(operator.add, other, self)

    def __rsub__(self, other):
        return BinaryExpression(operator.sub, other, self)

    def __rmul__(self, other):
        return BinaryExpression(operator.mul, other, self)

    def __rfloordiv__(self, other):
        return BinaryExpression(operator.floordiv, other, self)

    def __rtruediv__(self, other):
        return BinaryExpression(operator.truediv, other, self)

    def __rmod__(self, other):
        return BinaryExpression(operator.mod, other, self)

    def __rpow__(self, other):
        return BinaryExpression(operator.pow, other, self)

    def __rxor__(self, other):
        return BinaryExpression(operator.xor, other, self)

    def __rand__(self, other):
        return BinaryExpression(operator.and_, other, self)

    def __ror__(self, other):
        return BinaryExpression(operator.or_, other, self)

    def __rrshift__(self, other):
        return BinaryExpression(operator.rshift, other, self)

    def __rlshift__(self, other):
        return BinaryExpression(operator.lshift, other, self)

    def __neg__(self):
        return UnaryExpression("neg", operator.neg, self)

    def __pos__(self):
        return UnaryExpression("pos", operator.pos, self)

    def __invert__(self):
        return UnaryExpression("invert", operator.not_, self)

    def __contains__(self, other):
        return BinaryExpression(operator.contains, self, other)

    def __gt__(self, other):
        return BinaryExpression(operator.gt, self, other)

    def __ge__(self, other):
        return BinaryExpression(operator.ge, self, other)

    def __lt__(self, other):
        return BinaryExpression(operator.lt, self, other)

    def __le__(self, other):
        return BinaryExpression(operator.le, self, other)

    def __eq__(self, other):
        return BinaryExpression(operator.eq, self, other)

    def __ne__(self, other):
        return BinaryExpression(operator.ne, self, other)


class ConditionContext:
    """Class implementation of an inline condition.

    Use this class to automatically apply a condition to multiple
    field definitions. Note that this class will only work if it
    has access to the parent stack frame.

    .. code-block:: python

        @struct
        class Format:
            magic: b"MGK"
            length: uint32

            with this.length > 32:
                # other field definitions here
                foo: uint8

    This class will **replace** any existing fields!

    :param condition: a context lambda or constant boolean value
    :type condition: Union[_ContextLambda, bool]
    """

    __slots__ = "func", "annotations", "namelist", "depth"

    def __init__(self, condition: Union[_ContextLambda, bool], depth=2):
        if (sys.version_info.major, sys.version_info.minor) >= (3, 14):
            warnings.warn(
                "Python3.14 breaks support for Contitional fields. Conditional "
                "statements must be defined manually until a fix has been released."
            )
        self.func = condition
        self.annotations = None
        self.namelist = None
        self.depth = depth

    def getframe(self, num: int, msg=None) -> FrameType:
        try:
            return sys._getframe(num)
        except AttributeError as exc:
            raise StructException(msg) from exc

    def __enter__(self) -> Self:
        frame = self.getframe(self.depth, "Could not enter condition context!")
        # keep track of all annotations
        try:
            self.annotations = frame.f_locals["__annotations__"]
        except AttributeError as exc:
            module = frame.f_locals.get("__module__")
            qualname = frame.f_locals.get("__qualname__")
            msg = f"Could not get annotations in {module} (context={qualname!r})"
            raise StructException(msg) from exc

        # store names before new fields are added
        self.namelist = list(self.annotations)
        return self

    def __exit__(self, *_) -> None:
        # pylint: disable-next=import-outside-toplevel
        from caterpillar.fields import Field

        new_names = set(self.annotations) - set(self.namelist)
        for name in new_names:
            # modify newly created fields
            field = self.annotations[name]
            if isinstance(field, Field):
                # field already defined/created -> check for condition
                if field.has_condition():
                    # the field's condition AND this one must be true
                    field.condition = BinaryExpression(
                        operator.and_, field.condition, self.func
                    )
                else:
                    field //= self.func
            else:
                # create a field (other attributes will be modified later)

                # ISSUE #15: The annotation must be converted to a _StructLike
                # object. In case we have struct classes, the special __struct__
                # attribute must be used.
                struct_obj = to_struct(field)
                if not isinstance(struct_obj, Field):
                    struct_obj = Field(struct_obj)

                struct_obj.condition = self.func
                self.annotations[name] = struct_obj

        self.annotations = None
        self.namelist = None


@dataclass(repr=False)
class BinaryExpression(ExprMixin):
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
        return f"{self.operand.__name__}{{{self.left!r}, {self.right!r}}}"

    def __enter__(self):
        # pylint: disable-next=attribute-defined-outside-init
        self._cond = ConditionContext(self, depth=3)
        self._cond.__enter__()
        return self

    def __exit__(self, *_):
        self._cond.__exit__(*_)


@dataclass
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
        return f"{self.operand.__name__}{{{self.value!r}}}"

    def __enter__(self):
        # pylint: disable-next=attribute-defined-outside-init
        self._cond = ConditionContext(self, depth=3)
        self._cond.__enter__()
        return self

    def __exit__(self, *_):
        self._cond.__exit__(*_)


class ContextPath(ExprMixin):
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

    def __call__(self, context: _ContextLike = None, **kwds):
        """
        Calls the lambda function to retrieve a value from a Context.

        :param context: The Context from which to retrieve the value.
        :param kwds: Additional keyword arguments.
        :return: The value retrieved from the Context based on the path.
        """
        if context is None:
            self._ops_.append((operator.call, (), kwds))
            return self
        value = context.__context_getattr__(self.path)
        for operation, args, kwargs in self._ops_:
            value = operation(value, *args, **kwargs)
        return value

    def __getitem__(self, key) -> Self:
        self._ops_.append((operator.getitem, (key,), {}))
        return self

    def __type__(self) -> type:
        return Any

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
        extra = []
        for operation, args, kwargs in self._ops_:
            data = []
            if len(args) > 0:
                data.append(*map(repr, args))
            if len(kwargs) > 0:
                data.append(*[f"{x}={y!r}" for x, y in kwargs.items()])
            extra.append(f"{operation.__name__}({', '.join(data)})")

        if len(extra) == 0:
            return f"Path({self.path!r})"

        return f"Path({self.path!r}, {', '.join(extra)})"

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


class ContextLength(ExprMixin):
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

    def __repr__(self) -> str:
        return f"len({self.path!r})"


this = ContextPath(CTX_OBJECT)
ctx = ContextPath()
parent = ContextPath(".".join([CTX_PARENT, CTX_OBJECT]))
