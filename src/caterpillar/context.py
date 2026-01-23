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
from __future__ import annotations

import operator
import sys
import warnings

from typing import Callable, Any, Generic, Protocol
from typing_extensions import Final, Self, override, TypeVar
from types import FrameType, TracebackType
from dataclasses import dataclass

from caterpillar.exception import StructException
from caterpillar.registry import to_struct
from caterpillar.options import Flag
from caterpillar.abc import _ContextLike, _ContextLambda, _IT, _ContextFactoryLike


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
CTX_ROOT = "_root"
CTX_ORDER = "_order"


class Context(dict[str, Any]):
    """Represents a context object with attribute-style access."""

    @override
    def __setattr__(self, key: str, value: Any, /) -> None:
        """
        Sets an attribute in the context.

        :param key: The attribute key.
        :param value: The value to be set.
        """
        self[key] = value

    @override
    def __getattribute__(self, key: str) -> Any:
        """
        Retrieves an attribute from the context.

        :param key: The attribute key.
        :return: The value associated with the key.
        """
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return self.__context_getattr__(key)

    def __context_getattr__(self, path: str) -> Any:
        """
        Retrieves an attribute from the context.

        :param key: The attribute key.
        :return: The value associated with the key.
        """
        nodes = path.split(".")
        obj: Any = (
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
        return self.get("_root", self)  # pyright: ignore[reportAny]


O_CONTEXT_FACTORY: Flag[_ContextFactoryLike] = (
    Flag(  # pyright: ignore[reportAssignmentType]
        "option.context_factory", value=Context
    )
)


class SetContextVar(Generic[_IT]):
    """Defines an action that sets a context variable during pack or unpack.

    The value assigned to the context key is computed dynamically using
    a user-provided callable evaluated at runtime.

    :param key: Name of the context variable to set
    :type key: str
    :param func: Callable used to compute the context value
    :type func: callable
    """

    def __init__(self, key: str, func: _ContextLambda[_IT]) -> None:
        self.key: str = key
        self.func: _ContextLambda[_IT] = func

    def __action_pack__(self, context: _ContextLike) -> None:
        """Apply the context variable assignment during packing.

        The callable is evaluated and its result is stored in the
        context under the configured key.

        :param context: Active packing context
        :type context: object
        :return: None
        :rtype: None
        """
        context.__context_setattr__(self.key, self.func(context))

    def __action_unpack__(self, context: _ContextLike) -> None:
        """Apply the context variable assignment during unpacking.

        The callable is evaluated and its result is stored in the
        context under the configured key.

        :param context: Active unpacking context
        :type context: object
        :return: None
        :rtype: None
        """
        context.__context_setattr__(self.key, self.func(context))


class ExprMixin:
    """
    A mixin class providing methods for creating binary and unary expressions.
    """

    def __add__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.add, self, other)

    def __sub__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.sub, self, other)

    def __mul__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.mul, self, other)

    def __floordiv__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.floordiv, self, other)

    def __truediv__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.truediv, self, other)

    def __mod__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.mod, self, other)

    def __pow__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.pow, self, other)

    def __xor__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.xor, self, other)

    def __and__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.and_, self, other)

    def __or__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.or_, self, other)

    def __rshift__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.rshift, self, other)

    def __lshift__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.lshift, self, other)

    __div__ = __truediv__  # pyright: ignore[reportUnannotatedClassAttribute]

    def __radd__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.add, other, self)

    def __rsub__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.sub, other, self)

    def __rmul__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.mul, other, self)

    def __rfloordiv__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.floordiv, other, self)

    def __rtruediv__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.truediv, other, self)

    def __rmod__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.mod, other, self)

    def __rpow__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.pow, other, self)

    def __rxor__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.xor, other, self)

    def __rand__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.and_, other, self)

    def __ror__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.or_, other, self)

    def __rrshift__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.rshift, other, self)

    def __rlshift__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.lshift, other, self)

    def __neg__(self):
        return UnaryExpression("neg", operator.neg, self)

    def __pos__(self):
        return UnaryExpression("pos", operator.pos, self)

    def __invert__(self):
        return UnaryExpression("invert", operator.not_, self)

    def __contains__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.contains, self, other)

    def __gt__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.gt, self, other)

    def __ge__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.ge, self, other)

    def __lt__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.lt, self, other)

    def __le__(self, other: object) -> BinaryExpression:
        return BinaryExpression(operator.le, self, other)

    @override
    def __eq__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: object
    ) -> BinaryExpression:
        return BinaryExpression(operator.eq, self, other)

    @override
    def __ne__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: object
    ) -> BinaryExpression:
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

    __slots__: tuple[str, str, str, str] = (
        "func",
        "annotations",
        "namelist",
        "depth",
    )

    def __init__(self, condition: _ContextLambda[bool], depth: int = 2):
        self.func: _ContextLambda[bool] = condition
        self.annotations: dict[str, Any] = {}
        self.namelist: list[str] = list()
        self.depth: int = depth

    def getframe(self, num: int, msg: str) -> FrameType:
        try:
            return sys._getframe(num)
        except AttributeError as exc:
            raise StructException(msg) from exc

    def __enter__(self) -> Self:
        if (sys.version_info.major, sys.version_info.minor) >= (3, 14):
            warnings.warn(
                "Python3.14 breaks support for Contitional fields. Conditional "
                + "statements must be defined manually until a fix has been released."
            )
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

    def __exit__(
        self, exc_type: type, exc_value: Exception, traceback: TracebackType
    ) -> None:
        # pylint: disable-next=import-outside-toplevel
        from caterpillar.fields import Field

        new_names = set(self.annotations) - set(self.namelist)
        for name in new_names:
            # modify newly created fields
            field: object = self.annotations[name]  # pyright: ignore[reportAny]
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

        self.annotations = dict()
        self.namelist = list()


@dataclass(repr=False)
class BinaryExpression(ExprMixin):
    """
    Represents a binary expression.

    :param operand: The binary operator function.
    :param left: The left operand.
    :param right: The right operand.
    """

    operand: Callable[[Any, Any], bool]
    left: Any | _ContextLambda[Any]
    right: Any | _ContextLambda[Any]

    def __call__(self, context: _ContextLike) -> bool:
        lhs = self.left(context) if callable(self.left) else self.left
        rhs = self.right(context) if callable(self.right) else self.right
        return self.operand(lhs, rhs)

    @override
    def __repr__(self) -> str:
        return f"{self.operand.__name__}{{{self.left!r}, {self.right!r}}}"

    def __enter__(self):
        # fmt: off
        self._cond: ConditionContext = ConditionContext(self, depth=3)  # pyright: ignore[reportUninitializedInstanceVariable]
        self._cond.__enter__()  # pyright: ignore[reportUnusedCallResult]
        return self
        # fmt: on

    def __exit__(self, exc_type: type, exc_value: Exception, traceback: TracebackType):
        self._cond.__exit__(exc_type, exc_value, traceback)


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
    value: Any | _ContextLambda[Any]

    def __call__(self, context: _ContextLike) -> Any:
        value = self.value(context) if callable(self.value) else self.value
        return self.operand(value)

    @override
    def __repr__(self) -> str:
        return f"{self.operand.__name__}{{{self.value!r}}}"

    def __enter__(self):
        # fmt: off
        self._cond: ConditionContext = ConditionContext(self, depth=3)  # pyright: ignore[reportUninitializedInstanceVariable]
        self._cond.__enter__()  # pyright: ignore[reportUnusedCallResult]
        return self
        # fmt: on

    def __exit__(self, exc_type: type, exc_value: Exception, traceback: TracebackType):
        self._cond.__exit__(exc_type, exc_value, traceback)


# fmt: off
class _ContextPathOp(Protocol):
    __name__: str
    def __call__(self, *args: Any, **kwds: Any) -> Any: ...  # pyright: ignore[reportAny]
# fmt: on


_T = TypeVar("_T")


class ContextPath(Generic[_T], ExprMixin):
    """
    Represents a lambda function for retrieving a value from a Context based on a specified path.
    """

    # internal set of operations to apply
    _ops_: list[tuple[_ContextPathOp, list[Any], dict[str, Any]]]

    def __init__(self, path: str | None = None) -> None:
        """
        Initializes a ContextPath instance with an optional path.

        :param path: The path to use when retrieving a value from a Context.
        """
        self.path: str | None = path
        self._ops_ = list()
        self.call_kwargs: dict[str, Any] = dict()
        self.getitem_args: list[Any] = list()

    def __call__(self, context: _ContextLike) -> _T:
        """
        Calls the lambda function to retrieve a value from a Context.

        :param context: The Context from which to retrieve the value.
        :param kwds: Additional keyword arguments.
        :return: The value retrieved from the Context based on the path.
        """
        # REVISIT: find a way to implement calls
        if context is None:
            self._ops_.append((operator.call, [], kwds))
            return self

        if self.path is None:  # no path configured, just return the context itself
            return context

        value = context.__context_getattr__(self.path)
        for operation, args, kwargs in self._ops_:
            value = operation(value, *args, **kwargs)
        return value

    def __getitem__(self, key: str) -> Self:
        self._ops_.append((operator.getitem, [key], {}))
        return self

    def __type__(self) -> type:
        return object

    @override
    def __getattribute__(self, key: str) -> ContextPath[_IT]:
        """
        Gets an attribute from the ContextPath, creating a new instance if needed.

        :param key: The attribute key.
        :return: A new ContextPath instance with an updated path.
        """
        try:
            return super().__getattribute__(key)  # pyright: ignore[reportAny]
        except AttributeError:
            if not self.path:
                return ContextPath(key)
            return ContextPath(".".join([self.path, key]))

    @override
    def __repr__(self) -> str:
        """
        Returns a string representation of the ContextPath.

        :return: A string representation.
        """
        extra: list[str] = []
        for operation, args, kwargs in self._ops_:
            data: list[str] = []
            if len(args) > 0:
                data.append(*map(repr, args))
            if len(kwargs) > 0:
                data.append(*[f"{x}={y!r}" for x, y in kwargs.items()])
            extra.append(f"{operation.__name__}({', '.join(data)})")

        if len(extra) == 0:
            return f"Path({self.path!r})"

        return f"Path({self.path!r}, {', '.join(extra)})"

    @override
    def __str__(self) -> str:
        """
        Returns a string representation of the path.

        :return: A string representation of the path.
        """
        return self.path or ""

    @property
    def parent(self) -> ContextPath:
        path = f"{CTX_PARENT}.{CTX_OBJECT}"
        if not self.path:
            return ContextPath(path)
        return ContextPath(".".join([self.path, path]))


class ContextLength(ExprMixin):
    def __init__(self, path: ContextPath) -> None:
        self.path: ContextPath = path

    def __call__(self, context: _ContextLike | None = None, **kwds: Any):
        """
        Calls the lambda function to retrieve a value from a Context.

        :param context: The Context from which to retrieve the value.
        :param kwds: Additional keyword arguments (ignored in this implementation).
        :return: The value retrieved from the Context based on the path.
        """
        return len(self.path(context))  # pyright: ignore[reportArgumentType]

    @override
    def __repr__(self) -> str:
        return f"len({self.path!r})"

# fmt: off
this: Final[ContextPath[_ContextLike]] = ContextPath(CTX_OBJECT)
ctx: Final[ContextPath[_ContextLike]] = ContextPath()
parent: Final[ContextPath[_ContextLike]] = ContextPath(".".join([CTX_PARENT, CTX_OBJECT]))
root: Final[ContextPath[_ContextLike]] = ContextPath(CTX_ROOT)
