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
# pyright: reportPrivateUsage=false
from types import TracebackType
from typing import Any
from typing_extensions import override, Self

from caterpillar.context import ConditionContext
from caterpillar.exception import ValidationError
from caterpillar.shared import typeof, constval
from caterpillar.abc import _ContextLambda, _ContextLike, _StructLike

from ._base import Field


class ConditionalChain:
    """Simplistic conditional chain that represents if-else statements.

    Using this class we can introduce conditional statements into our
    class definition. While this class can't be used in class definitions,
    it may be used outside of them.

    For conditional statements in class definitions, see
    :class:`~caterpillar.fields.conditional.If`,
    :class:`~caterpillar.fields.conditional.ElseIf` or
    :class:`~caterpillar.fields.conditional.Else`.
    """

    __slots__: tuple[str, ...] = "chain", "conditions"

    def __init__(
        self, struct: _StructLike, condition: _ContextLambda[bool] | bool
    ) -> None:
        self.chain: dict[int, _StructLike] = {}
        self.conditions: list[_ContextLambda[bool] | None] = []
        self.add(struct, condition)

    def __type__(self) -> type | str | None:
        target_type = None
        for struct_ty in self.chain.values():
            target_type = target_type | typeof(struct_ty)

        return target_type  # pyright: ignore[reportReturnType]

    @override
    def __repr__(self) -> str:
        annotation: list[str] = []
        count = len(self.chain)
        for i, entry in enumerate(self.chain.items()):
            func_idx, struct = entry
            func = self.conditions[func_idx]
            if i != count - 1 or func is not None:
                annotation.append(f"{struct.__type__()} if {func!r}")
            else:
                annotation.append(f"else {struct.__type__()}")

        return f"<Chain {', '.join(annotation)}>"

    def add(self, struct: _StructLike, func: _ContextLambda[bool] | bool) -> None:
        idx: int = len(self.chain)
        self.chain[idx] = struct
        if isinstance(func, bool):
            func = constval(func)
        self.conditions.append(func)

    def get_struct(self, context: _ContextLike) -> _StructLike | None:
        index = 0
        while index < len(self.chain):
            func = self.conditions[index]
            if func is None or func(context):
                return self.chain[index]
            index += 1

    def __unpack__(self, context: _ContextLike) -> object:
        struct = self.get_struct(context)
        return struct.__unpack__(context) if struct else None

    def __pack__(self, obj: object, context: _ContextLike) -> None:
        struct = self.get_struct(context)
        if struct:
            struct.__pack__(obj, context)

    def __size__(self, context: _ContextLike) -> int:
        struct = self.get_struct(context)
        return struct.__size__(context) if struct else 0


class If(ConditionContext):
    """If-statement implementation for class definitions.

    .. versionchanged:: 2.4.5

        Python 3.14 is **not** supported.

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with If(lambda _: GLOBAL_CONSTANT == 33):
                b: uint8

    Note that this class will alter the used fields and cover multiple
    field definitions. In addition, the type annotation will be modified
    to display the condition as well.

    .. note::
        This class is **not** a struct, but a simple context manager.
    """

    # As this class essentially does the same as ConditionContext,
    # we don't have to implement anything. A simple if-statment
    # is using the built-in conditional execution model from the Field
    # class.

# TODO(REVISIT): fix Annotated[...] annotation handling
class ElseIf(ConditionContext):
    """ElseIf-statement implementation for class definitions.

    .. versionchanged:: 2.4.3

        Python 3.14 is **not** supported.

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with this.a == 32:
                ...

            with ElseIf(this.a == 34):
                ...
    """

    @override
    def __enter__(self) -> Self:
        self.depth: int = 3
        super().__enter__()  # pyright: ignore[reportUnusedCallResult]
        self.depth = 2
        # We have to copy all variables here as we want to
        # provide the possibility to re-define some fields.
        self.annotations: dict[str, Any] = self.annotations.copy()
        return self

    @override
    def __exit__(self, exc_type: type, exc_value: Exception, traceback: TracebackType):
        # fmt: off
        # we have to inspect no only new names but also defined ones
        frame = self.getframe(self.depth, "Could not enter condition context!")
        annotations: dict[str, _StructLike] = frame.f_locals["__annotations__"]  # pyright: ignore[reportAny]

        # inspect defined fields
        for name in set(annotations) & set(self.namelist):
            new_field = annotations[name]
            field: _StructLike = self.annotations[name]  # pyright: ignore[reportAny]
            if field is not new_field:
                # We can assume that the old field is already an instance
                # of Field, otherwise it would have been defined outside
                # the previous condition.
                if not isinstance(field, (Field, ConditionalChain)):
                    msg = (
                        f"The field {name!r} does not appear to be defined in a "
                        "previous condition context. It can't be defined twice!"
                    )
                    raise ValidationError(msg)
                if not isinstance(field, ConditionalChain):
                    # it MUST store a condition
                    if not field.has_condition():
                        msg = (
                            "A field defined outside a condition context can't be "
                            f"overridden in such. (field={name!r})"
                        )
                        raise ValidationError(msg)

                    new_struct = ConditionalChain(field, field.condition)
                    # Reset field's condition
                    field.condition = True
                else:
                    new_struct = field
                new_struct.add(new_field, self.func)
                annotations[name] = new_struct

        # inspect new fields
        self.annotations = annotations
        super().__exit__(exc_type, exc_value, traceback)


# REVISIT: There is one case where 'ELSE' is not applicable and will cause
# a field to be present at all times. This problem exists if we add fields
# into an else-branch without a previously defined field.
Else = ElseIf(lambda context: True)
