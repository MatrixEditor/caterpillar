# Copyright (C) MatrixEditor 2023-2026
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
# pyright: reportPrivateUsage=false, reportExplicitAny=false, reportUnreachable=false
# pyright: reportAny=false
import operator
import sys
from types import TracebackType
from typing import Annotated, Any, get_args, get_origin

from typing_extensions import Final, Self, override

from caterpillar.abc import (_AnnotationT, _ArchLike, _ContextLambda,
                             _ContextLike, _EndianLike, _OptionLike,
                             _StructLike)
from caterpillar.context import (BinaryExpression, ConditionContext,
                                 UnaryExpression)
from caterpillar.exception import StructException, ValidationError
from caterpillar.registry import to_struct
from caterpillar.shared import constval, iscond, iscondend, iscondstart, typeof

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


class _ConditionalAnnotation:
    __slots__: tuple[str, ...] = ("condition", "branch_conditions", "is_last")

    __conditional__: bool = True

    def __init__(
        self,
        condition: _ContextLambda[bool] | bool,
        branch_conditions: tuple[_ContextLambda[bool] | bool, ...] | None = None,
        *,
        is_last: bool = False,
    ) -> None:
        self.condition: _ContextLambda[bool] | bool = condition
        self.branch_conditions: (
            tuple[_ContextLambda[bool] | bool, ...] | tuple[_ContextLambda[bool] | bool]
        ) = branch_conditions or (condition,)
        self.is_last: bool = is_last

    def __getitem__(self, annotation: _AnnotationT) -> _AnnotationT:
        return _ConditionalAnnotation.apply_condition(annotation, self.condition)

    @staticmethod
    def apply_condition(
        annotation: _AnnotationT, condition: _ContextLambda[bool] | bool
    ) -> _AnnotationT:
        annotated_type = None
        extra_options = ()
        field = annotation
        is_annotated = get_origin(annotation) is Annotated
        if is_annotated:
            annotated_type, field, *extra_options = get_args(annotation)

        if not isinstance(field, Field):
            struct_obj = to_struct(field)
            if not isinstance(struct_obj, Field):
                struct_obj = Field(struct_obj)
            struct_obj.condition = condition
            field = struct_obj
        elif field.has_condition():
            field.condition = BinaryExpression(
                operator.and_, field.condition, condition
            )
        else:
            field //= condition  # pyright: ignore[reportUnknownVariableType]

        return (
            Annotated[(annotated_type, field, *extra_options)]
            if is_annotated
            else field
        )


class Start:
    """Start marker for an inline explicit conditional block.

    Use this as metadata on the first real field in a Python 3.14+ conditional
    block:

    .. code-block:: python

        with If(this.flag == 1) as when:
            first: f[int, uint8, Start(when)]
            second: f[int, uint8]
            last: f[int, uint8, End(when)]

    Unlike the older invisible marker-field spelling, this does not add a
    synthetic field to the class body.

    .. versionadded: 2.9.0
    """

    __slots__: tuple[str, ...] = ("marker", "condition", "branch_conditions", "is_last")

    __conditional__: bool = True
    __conditional_start__: bool = True

    def __init__(self, marker: "_MarkerT") -> None:
        condition = getattr(marker, "condition", getattr(marker, "func", None))
        if condition is None:
            raise StructException(
                "Start() requires a conditional marker returned by If."
            )
        self.marker: _MarkerT = marker
        self.condition: _ContextLambda[bool] | bool = condition
        self.branch_conditions: tuple[_ContextLambda[bool] | bool, ...] = getattr(
            marker, "branch_conditions", (condition,)
        )
        self.is_last: bool = getattr(marker, "is_last", False)


class End:
    """End marker for an explicit conditional block.

    Use this as metadata on the last real field in a Python 3.14+ inline marker
    block:

    .. code-block:: python

        with If(this.flag == 1) as when:
            first: f[int, uint8, Start(when)]
            second: f[int, uint8]
            last: f[int, uint8, End(when)]

    The older invisible marker-field spelling is still supported:

    .. code-block:: python

        with If(this.flag == 1) as when:
            _: f[None, when] = Invisible()
            value: f[int, uint8]
            _end: f[None, End(when)] = Invisible()

    Invisible marker fields are removed from the final struct model.

    .. versionadded: 2.9.0
    """

    __slots__: tuple[str, ...] = ("marker", "condition")

    __conditional__: bool = True
    __conditional_end__: bool = True

    def __init__(self, marker: "_MarkerT") -> None:
        condition = getattr(marker, "condition", getattr(marker, "func", None))
        if condition is None:
            raise StructException("End() requires a conditional marker returned by If.")
        self.marker: _MarkerT = marker
        self.condition: _ContextLambda[bool] | bool = condition


_MarkerT = _ConditionalAnnotation | ConditionContext | Start | End


def and_cond(
    left: _ContextLambda[bool] | bool, right: _ContextLambda[bool] | bool
) -> _ContextLambda[bool] | bool:
    if left is True:
        return right
    if right is True:
        return left
    if left is False or right is False:
        return False
    return BinaryExpression(operator.and_, left, right)


def or_cond(
    left: _ContextLambda[bool] | bool, right: _ContextLambda[bool] | bool
) -> _ContextLambda[bool] | bool:
    if left is True or right is True:
        return True
    if left is False:
        return right
    if right is False:
        return left
    return BinaryExpression(operator.or_, left, right)


def not_cond(
    condition: _ContextLambda[bool] | bool,
) -> _ContextLambda[bool] | bool:
    if condition is True:
        return False
    if condition is False:
        return True
    return UnaryExpression("not", operator.not_, condition)


def any_cond(
    conditions: tuple[_ContextLambda[bool] | bool, ...],
) -> _ContextLambda[bool] | bool:
    result: _ContextLambda[bool] | bool = False
    for condition in conditions:
        result = or_cond(result, condition)
    return result


def _previous_branch_conditions(
    marker: ConditionContext | _ConditionalAnnotation,
) -> tuple[_ContextLambda[bool] | bool, ...]:
    if iscondend(marker):
        raise StructException(
            "Conditional branch requires a start marker, not End(...)."
        )
    conditions = getattr(marker, "branch_conditions", None)
    if not conditions:
        raise StructException(
            "Conditional branch requires a marker returned by 'with If(...) as name'."
        )
    return conditions


def ensure_not_last(
    marker: ConditionContext | _ConditionalAnnotation, label: str
) -> None:
    if getattr(marker, "is_last", False):
        raise StructException(f"{label} cannot be added after Else.")


def chain_cond(
    previous: ConditionContext, condition: _ContextLambda[bool] | bool
) -> tuple[_ContextLambda[bool] | bool, tuple[_ContextLambda[bool] | bool, ...]]:
    ensure_not_last(previous, "ElseIf")
    previous_conditions = _previous_branch_conditions(previous)
    effective = and_cond(not_cond(any_cond(previous_conditions)), condition)
    return effective, (*previous_conditions, condition)


def else_cond(
    previous: ConditionContext,
) -> tuple[_ContextLambda[bool] | bool, tuple[_ContextLambda[bool] | bool, ...]]:
    ensure_not_last(previous, "Else")
    previous_conditions = _previous_branch_conditions(previous)
    return not_cond(any_cond(previous_conditions)), previous_conditions


def _split_conditional_metadata(
    annotation: Any,
) -> tuple[Any, list[Any], bool]:
    if get_origin(annotation) is not Annotated:
        return annotation, [], False

    args = get_args(annotation)
    if not args:
        return annotation, [], False

    annotated_type, *metadata = args
    markers = [value for value in metadata if iscond(value)]
    if not markers:
        return annotation, [], False

    kept_metadata = [value for value in metadata if not iscond(value)]
    marker_field = annotated_type in (None, type(None)) and not kept_metadata
    cleaned = (
        Annotated[(annotated_type, *kept_metadata)] if kept_metadata else annotated_type
    )
    return cleaned, markers, marker_field


def _open_marker(
    model: type,
    name: str,
    marker: Any,
    active: list[list[Any]],
    seen_starts: set[int],
) -> None:
    target: _MarkerT = getattr(marker, "marker", marker)
    marker_id = id(target)
    if sys.version_info >= (3, 14) and marker_id in seen_starts:
        raise StructException(
            f"Conditional marker {name!r} in {model!r} reuses a marker "
            + "alias. Use a unique alias for each Python 3.14 marker block."
        )
    seen_starts.add(marker_id)
    active.append([target, 0])


def _close_marker(
    model: type, name: str, marker: _MarkerT, active: list[list[Any]]
) -> None:
    if not active:
        raise StructException(
            f"Conditional end marker {name!r} in {model!r} has no "
            + "matching start marker."
        )
    expected = getattr(marker, "marker", marker)
    current, field_count = active[-1]
    if current is not expected:
        raise StructException(
            f"Conditional end marker {name!r} in {model!r} does not "
            + "match the active conditional marker."
        )
    if field_count == 0:
        raise StructException(
            f"Conditional marker ending at {name!r} in {model!r} does "
            + "not contain any fields. Repeated field names in marker "
            + "branches are not supported; use Branch(...) for same-field "
            + "conditional chains."
        )
    _ = active.pop()


def apply_conditional_markers(
    model: type, annotations: dict[str, _AnnotationT]
) -> tuple[dict[str, Any], set[str]]:
    updated: dict[str, Any] = {}
    removed: set[str] = set()
    active: list[list[Any]] = []
    seen_starts: set[int] = set()

    for name, annotation in annotations.items():
        annotation, markers, marker_field = _split_conditional_metadata(annotation)
        if marker_field:
            removed.add(name)
            for marker in markers:
                if iscondend(marker):
                    _close_marker(model, name, marker, active)
                else:
                    _open_marker(model, name, marker, active, seen_starts)
            continue

        start_markers = [marker for marker in markers if iscondstart(marker)]
        end_markers = [marker for marker in markers if iscondend(marker)]
        field_markers = [
            marker
            for marker in markers
            if not iscondstart(marker) and not iscondend(marker)
        ]

        for marker in start_markers:
            _open_marker(model, name, marker, active, seen_starts)

        if sys.version_info >= (3, 14):
            for entry in active:
                conditional = entry[0]
                annotation = _ConditionalAnnotation.apply_condition(
                    annotation, conditional.condition
                )
            for marker in field_markers:
                annotation = _ConditionalAnnotation.apply_condition(
                    annotation, marker.condition
                )
        for entry in active:
            entry[1] += 1
        updated[name] = annotation

        for marker in end_markers:
            _close_marker(model, name, marker, active)

    if active:
        raise StructException(
            f"Conditional marker in {model!r} is missing an End(when) marker."
        )

    return updated, removed


class When:
    """One conditional arm for :class:`Branch`.

    :param condition: Context expression controlling this arm.
    :param annotation: Field annotation or struct selected when the condition
        evaluates to true.

    .. versionadded:: 2.9.0
    """

    __slots__: tuple[str, ...] = ("condition", "annotation")

    def __init__(
        self, condition: _ContextLambda[bool] | bool, annotation: _AnnotationT
    ) -> None:
        self.condition: _ContextLambda[bool] | bool = condition
        self.annotation: _AnnotationT = annotation


class Otherwise:
    """Fallback arm for :class:`Branch`.

    The fallback arm is selected when no earlier :class:`When` condition matched.
    A branch can contain at most one fallback arm, and it must appear last.

    .. versionadded:: 2.9.0
    """

    __slots__: tuple[str, ...] = ("annotation",)

    def __init__(self, annotation: _AnnotationT) -> None:
        self.annotation: _AnnotationT = annotation


class Branch:
    """Conditional field chain for one attribute.

    Use this when several conditions should decode or encode the same Python
    attribute with different field definitions.

    .. code-block:: python

        @struct
        class Packet:
            tag: f[int, uint8]
            value: f[
                int,
                Branch(
                    When(this.tag == 1, uint8),
                    When(this.tag == 2, uint16),
                    Otherwise(uint8),
                ),
            ]

    Arm annotations can use ``f[...]`` to carry local options such as byte order.

    .. versionadded:: 2.9.0
    """

    __slots__: tuple[str, ...] = ("chain",)

    def __init__(self, *arms: When | Otherwise) -> None:
        if not arms:
            raise StructException(
                "Branch() requires at least one When or Otherwise arm."
            )

        chain: ConditionalChain | None = None
        seen_otherwise = False
        for arm in arms:
            match arm:
                case When():
                    if seen_otherwise:
                        raise StructException(
                            "When(...) cannot appear after Otherwise(...)."
                        )
                    condition = arm.condition
                    annotation = arm.annotation
                case Otherwise():
                    if seen_otherwise:
                        raise StructException(
                            "Branch() can only contain one Otherwise(...)."
                        )
                    seen_otherwise = True
                    condition = None
                    annotation = arm.annotation
                case _:  # pyright: ignore[reportUnnecessaryComparison]
                    raise StructException(
                        f"Unsupported Branch arm {arm!r}; expected When or Otherwise."
                    )

            # create the struct
            options: list[_OptionLike | _EndianLike | _ArchLike] = []
            if get_origin(annotation) is Annotated:
                _, annotation, *options = get_args(annotation)

            struct_obj = (
                annotation if isinstance(annotation, Field) else to_struct(annotation)
            )
            if options:
                # This way we make sure no options are left out
                if not isinstance(struct_obj, Field):
                    struct_obj = Field(struct_obj)

                for option in options:
                    match option:
                        case _ArchLike():
                            struct_obj.arch = option
                        case _EndianLike():
                            struct_obj.order = option
                        case _OptionLike():
                            struct_obj.add_flag(option)
                        case _:  # pyright: ignore[reportUnnecessaryComparison]
                            raise ValidationError(
                                f"Could not add branch option: unsupported type ({type(option)})"
                            )

            if chain is None:
                chain = ConditionalChain(
                    struct_obj, True if condition is None else condition
                )
                if condition is None:
                    chain.conditions[-1] = None
            else:
                chain.add(struct_obj, condition)  # pyright: ignore[reportArgumentType]

        if chain is None:
            raise ValueError("Invalid number of arguments provided")

        self.chain: ConditionalChain = chain

    def __type__(self) -> type | str | None:
        return self.chain.__type__()

    def __unpack__(self, context: _ContextLike) -> object:
        return self.chain.__unpack__(context)

    def __pack__(self, obj: object, context: _ContextLike) -> None:
        self.chain.__pack__(obj, context)

    def __size__(self, context: _ContextLike) -> int:
        return self.chain.__size__(context)


class If(ConditionContext):
    """If-statement implementation for class definitions.

    .. versionchanged:: 2.9.0

        Python 3.14+ requires explicit conditional annotations using either
        ``with If(condition) as when:`` with ``field: f[type, field, when]`` for
        one field, inline ``Start(when)`` / ``End(when)`` metadata for a block,
        ``field: when[...]``, or explicit invisible marker fields.

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with If(lambda _: GLOBAL_CONSTANT == 33):
                b: uint8

    Python 3.14+ supports type-checker-friendly per-field metadata:

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with If(lambda _: GLOBAL_CONSTANT == 33) as when:
                b: f[int, uint8, when]

    It also supports inline block markers:

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with If(lambda _: GLOBAL_CONSTANT == 33) as when:
                b: f[int, uint8, Start(when)]
                c: uint8
                d: f[int, uint8, End(when)]

    Note that this class will alter the used fields and cover multiple
    field definitions. In addition, the type annotation will be modified
    to display the condition as well.

    .. note::
        This class is **not** a struct, but a simple context manager.
    """

    __slots__: tuple[str, ...] = ("_proxy",)
    __conditional__: bool = True

    def __init__(self, condition: _ContextLambda[bool], depth: int = 2):
        super().__init__(condition, depth)
        self._proxy: _ConditionalAnnotation | None = None

    @property
    def condition(self) -> _ContextLambda[bool] | bool:
        return self.func

    @property
    def branch_conditions(self) -> tuple[_ContextLambda[bool] | bool, ...]:
        return (self.func,)

    @property
    def is_terminal(self) -> bool:
        return False

    @override
    def __enter__(self) -> Self | _ConditionalAnnotation:
        if sys.version_info >= (3, 14):
            self._proxy = _ConditionalAnnotation(self.func, (self.func,))
            return self._proxy

        self._proxy = _ConditionalAnnotation(self.func)
        depth = self.depth
        self.depth: int = depth + 1
        try:
            return super().__enter__()
        finally:
            self.depth = depth

    def __getitem__(self, annotation: _AnnotationT) -> Any:
        if sys.version_info >= (3, 14):
            return _ConditionalAnnotation.apply_condition(annotation, self.func)
        return annotation

    @override
    def __exit__(
        self, exc_type: type, exc_value: Exception, traceback: TracebackType
    ) -> None:
        if sys.version_info >= (3, 14):
            frame = self.getframe(2, "Could not exit condition context!")
            if not any(value is self._proxy for value in frame.f_locals.values()):
                raise StructException(
                    "Implicit 'with If(condition):' blocks are not supported on "
                    + "Python 3.14+. Use 'with If(condition) as when:' with "
                    + "'field: f[type, field, when]' for one field, or "
                    + "'Start(when)' / 'End(when)' metadata for a block."
                )
            self._proxy = None
            return None
        depth = self.depth
        self.depth = depth + 1
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.depth = depth


# TODO(REVISIT): fix Annotated[...] annotation handling
class ElseIf(ConditionContext):
    """ElseIf-statement implementation for class definitions.

    Python <= 3.13 supports the legacy implicit form:

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with this.a == 32:
                ...

            with ElseIf(this.a == 34):
                ...

    Python 3.14+ requires the explicit marker form:

    .. code-block:: python

        @struct
        class Format:
            a: uint32

            with If(this.a == 32) as first:
                one: f[int, uint8, first]

            with ElseIf(first, this.a == 34) as second:
                two: f[int, uint8, second]
    """

    __slots__: tuple[str, ...] = (
        "_branch_conditions",
        "is_last",
        "_marker_mode",
        "_proxy",
    )

    def __init__(self, *args: ConditionContext | _ContextLambda[bool] | bool) -> None:
        self._proxy: _ConditionalAnnotation | None = None
        match len(args):
            case 1:
                if isinstance(args[0], ConditionContext):
                    raise TypeError("ElseIf requires a condition!")

                super().__init__(args[0])
                self._branch_conditions = (self.func,)
                self.is_last: bool = False
                self._marker_mode: bool = False
            case 2:
                previous, condition = args
                ensure_not_last(previous, "ElseIf")
                previous_conditions = _previous_branch_conditions(previous)
                effective = and_cond(not_cond(any_cond(previous_conditions)), condition)
                branch_conditions = (*previous_conditions, condition)
                super().__init__(effective)
                self._branch_conditions: tuple[_ContextLambda[bool] | bool, ...] = (
                    branch_conditions  # pyright: ignore[reportAttributeAccessIssue]
                )
                self.is_last = False
                self._marker_mode = True
            case _:
                raise TypeError(
                    "ElseIf expects either ElseIf(condition) or ElseIf(previous, condition)."
                )

    @property
    def condition(self) -> _ContextLambda[bool] | bool:
        return self.func

    @property
    def branch_conditions(self) -> tuple[_ContextLambda[bool] | bool, ...]:
        return self._branch_conditions

    @property
    def is_terminal(self) -> bool:
        return self.is_last

    @override
    def __enter__(self) -> Self | _ConditionalAnnotation:
        if self._marker_mode:
            self._proxy = _ConditionalAnnotation(
                self.func,
                self.branch_conditions,
                is_last=self.is_terminal,
            )
            return self._proxy
        if sys.version_info >= (3, 14):
            raise StructException(
                "Implicit 'with ElseIf(condition):' blocks are not supported on "
                + "Python 3.14+. Use 'with ElseIf(previous, condition) as when:' "
                + "alongside 'f[..., when]' for one field or Start/End metadata for a block."
            )
        self.depth: int = 3
        super().__enter__()  # pyright: ignore[reportUnusedCallResult]
        self.depth = 2
        # We have to copy all variables here as we want to
        # provide the possibility to re-define some fields.
        self.annotations: dict[str, _AnnotationT] = self.annotations.copy()
        return self

    @override
    def __exit__(self, exc_type: type, exc_value: Exception, traceback: TracebackType):
        if self._marker_mode:
            frame = self.getframe(2, "Could not exit condition context!")
            if not any(value is self._proxy for value in frame.f_locals.values()):
                raise StructException(
                    "Python 3.14+ ElseIf blocks require "
                    + "'with ElseIf(previous, condition) as when:' with "
                    + "'f[..., when]' for one field or Start/End metadata for a block."
                )
            self._proxy = None
            return None

        # fmt: off
        # we have to inspect no only new names but also defined ones
        frame = self.getframe(self.depth, "Could not enter condition context!")
        annotations: dict[str, _StructLike] = frame.f_locals["__annotations__"]  # pyright: ignore[reportAny]

        # inspect defined fields
        for name in set(annotations) & set(self.namelist):
            new_field = annotations[name]
            field: _AnnotationT = self.annotations[name]
            is_annotated = get_origin(field) is Annotated
            if is_annotated:
                # annotated_type = field.__origin__
                # field, *extra_options = field.__metadata__
                _, field, *_ = get_args(field)

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
class _ElseBranch(ConditionContext):
    __slots__: tuple[str, ...] = ("_branch_conditions", "_is_last", "_proxy")

    def __init__(self, previous: ConditionContext) -> None:
        effective, branch_conditions = else_cond(previous)
        super().__init__(effective)
        self._branch_conditions: tuple[_ContextLambda[bool] | bool, ...] = (
            branch_conditions
        )
        self._is_last: bool = True
        self._proxy: _ConditionalAnnotation | None = None

    @property
    def condition(self) -> _ContextLambda[bool] | bool:
        return self.func

    @property
    def branch_conditions(self) -> tuple[_ContextLambda[bool] | bool, ...]:
        return self._branch_conditions

    @property
    def is_last(self) -> bool:
        return self._is_last

    def __enter__(self) -> _ConditionalAnnotation:
        self._proxy = _ConditionalAnnotation(
            self.func,
            self.branch_conditions,
            is_last=self.is_last,
        )
        return self._proxy

    def __exit__(
        self, exc_type: type, exc_value: Exception, traceback: TracebackType
    ) -> None:
        frame = self.getframe(2, "Could not exit condition context!")
        if not any(value is self._proxy for value in frame.f_locals.values()):
            raise StructException(
                "Python 3.14+ Else blocks require 'with Else(previous) as when:' "
                + "with 'f[..., when]' for one field or Start/End metadata for a block."
            )
        self._proxy = None
        return None


class _Else:
    """Else marker factory.

    .. versionchanged:: 2.9.0
        Python <= 3.13 supports ``with Else:`` for legacy condition blocks. Python
        3.14+ requires ``with Else(previous) as when:`` with ``f[..., when]`` for
        one field or ``Start(when)`` / ``End(when)`` metadata for a block.
    """

    __slots__: tuple[str, ...] = ("_legacy",)

    def __init__(self) -> None:
        self._legacy: ConditionContext = ElseIf(lambda context: True)

    def __call__(self, previous: ConditionContext) -> _ElseBranch:
        return _ElseBranch(previous)

    def __enter__(self) -> ElseIf:
        if sys.version_info >= (3, 14):
            raise StructException(
                "Implicit 'with Else:' blocks are not supported on Python 3.14+. "
                + "Use 'with Else(previous) as when:' with 'f[..., when]' for one "
                + "field or Start/End metadata for a block."
            )
        return self._legacy.__enter__()  # pyright: ignore[reportReturnType]

    def __exit__(
        self, exc_type: type, exc_value: Exception, traceback: TracebackType
    ) -> None:
        return self._legacy.__exit__(exc_type, exc_value, traceback)


Else: Final[_Else] = _Else()
