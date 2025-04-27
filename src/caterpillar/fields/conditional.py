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
import sys
import warnings

from typing import Union, Any
from typing import Optional
from caterpillar.abc import _ContextLambda, _StructLike
from caterpillar.abc import _ContextLike, typeof
from caterpillar.context import ConditionContext
from caterpillar.exception import ValidationError

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

    __slots__ = "chain", "conditions"

    def __init__(self, struct: _StructLike, condition: _ContextLambda) -> None:
        if (sys.version_info.major, sys.version_info.minor) >= (3, 14):
            warnings.warn(
                "Python3.14 breaks support for Contitional fields. Conditional "
                "statements must be defined manually until a fix has been released."
            )
        self.chain = {}
        self.conditions = []
        self.add(struct, condition)

    def __type__(self) -> str:
        return Optional[Union[*map(typeof, self.chain.values())]]

    def __repr__(self) -> str:
        annotation = []
        count = len(self.chain)
        for i, entry in enumerate(self.chain.items()):
            func_idx, struct = entry
            func = self.conditions[func_idx]
            if i != count - 1 or func is not None:
                annotation.append(f"{struct.__type__()} if {func!r}")
            else:
                annotation.append(f"else {struct.__type__()}")

        return f"<Chain {', '.join(annotation)}>"

    def add(self, struct: _StructLike, func: _ContextLambda) -> None:
        idx = len(self.chain)
        self.chain[idx] = struct
        self.conditions.append(func)

    def get_struct(self, context: _ContextLike) -> Optional[_StructLike]:
        index = 0
        while index < len(self.chain):
            func = self.conditions[index]
            if func is None or func(context):
                return self.chain[index]
            index += 1

    def __unpack__(self, context: _ContextLike) -> Any:
        struct = self.get_struct(context)
        return struct.__unpack__(context) if struct else None

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
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

    def __enter__(self):
        self.depth = 3
        super().__enter__()
        self.depth = 2
        # We have to copy all variables here as we want to
        # provide the possibility to re-define some fields.
        self.annotations = self.annotations.copy()
        return self

    def __exit__(self, *_):
        # we have to inspect no only new names but also defined ones
        frame = self.getframe(self.depth, "Could not enter condition context!")
        annotations = frame.f_locals["__annotations__"]

        # inspect defined fields
        for name in set(annotations) & set(self.namelist):
            new_field = annotations[name]
            field = self.annotations[name]
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
        super().__exit__()


# REVISIT: There is one case where 'ELSE' is not applicable and will cause
# a field to be present at all times. This problem exists if we add fields
# into an else-branch without a previously defined field.
Else = ElseIf(lambda _: True)
