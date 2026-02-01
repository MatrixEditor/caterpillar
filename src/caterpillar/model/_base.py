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
# pyright: reportPrivateUsage=false, reportAny=false, reportExplicitAny=false
import re

from collections.abc import Iterable
from typing import Annotated, Any, Generic, get_args, get_origin
from typing_extensions import Self, override, TypeVar

from caterpillar.context import (
    CTX_FIELD,
    CTX_PATH,
    CTX_OBJECT,
    CTX_STREAM,
    CTX_SEQ,
    O_CONTEXT_FACTORY,
    Context,
)
from caterpillar.exception import StructException, ValidationError
from caterpillar.options import (
    S_DISCARD_CONST,
    S_DISCARD_UNNAMED,
    S_UNION,
    S_REPLACE_TYPES,
)
from caterpillar.fields import (
    Field,
    INVALID_DEFAULT,
    FieldMixin,
    Const,
)
from caterpillar._common import unpack_seq, pack_seq
from caterpillar.shared import (
    ATTR_ACTION_PACK,
    ATTR_ACTION_UNPACK,
    Action,
)
from caterpillar import registry
from caterpillar.abc import (
    _StructLike,
    _ContextLike,
    _OptionLike,
    _ContextLambda,
    _EndianLike,
    _ArchLike,
    _StreamType,
    _ActionLike,
)


class _Member:
    def __init__(
        self,
        name: str | None,
        field: Field,
        include: bool = False,
        is_action: bool = False,
    ):
        # fmt: off
        self.name: str = name or ""
        self.field: Field = field
        self.include: bool = include
        self.is_action: bool = is_action
        self.action_unpack: _ContextLambda[None] | None = getattr(field, ATTR_ACTION_UNPACK, None)
        self.action_pack: _ContextLambda[None] | None = getattr(field, ATTR_ACTION_PACK, None)

    @override
    def __repr__(self) -> str:
        if self.is_action:
            return f"Action({self.field})"

        return f"Member(name={self.name}, field={self.field}, include={self.include})"

    @override
    def __eq__(self, value: object, /) -> bool:
        return self.field == value or value == self.name


_SeqModelT = TypeVar("_SeqModelT", default=dict[str, Any])
_SeqOT = TypeVar("_SeqOT", default=dict[str, Any])
_SeqIT = TypeVar("_SeqIT", default=dict[str, Any])
_ExtraOptionT = _EndianLike | _ArchLike | _OptionLike[Any]
_AnnotationT = str | bytes | Field | type | _ActionLike | Any


class Sequence(Generic[_SeqModelT, _SeqIT, _SeqOT], FieldMixin[_SeqIT, _SeqOT]):
    """Default implementation for a sequence of fields.

    The native Python type mapped to this struct class is :code:`dict`. To convert
    a dictionary into a sequence, you can either use the contructor directly or apply
    the type converter for this class:

    >>> to_struct({'a': uint8})
    Sequence(fields=['a'])
    """

    __slots__: tuple[str, ...] = (
        "model",
        "fields",
        "order",
        "arch",
        "options",
        "field_options",
        "_members",
        "is_union",
    )

    def __init__(
        self,
        model: _SeqModelT,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> None:
        self.model: _SeqModelT = model
        self.arch: _ArchLike | None = arch
        self.order: _EndianLike | None = order
        self.options: set[_OptionLike] = set(options or [])
        self.field_options: set[_OptionLike] = set(field_options or [])

        # these fields will be set or used while processing the model type
        self._members: dict[str, Field] = {}
        self.fields: list[_Member] = []
        self.is_union: bool = S_UNION in self.options
        # Process all fields in the model
        self._process_model()

    def __add__(self, sequence: "Sequence[Any, Any, Any]") -> Self:
        # We will try to import all fields from the given sequence
        for member in sequence.fields:
            # Ignore duplicates here:
            if member.name in self.fields:
                continue

            self.fields.append(member)
            if member.include and not member.is_action:
                self._members[member.name] = member.field
        return self

    def __sub__(self, sequence: "Sequence") -> Self:
        # By default, we are only removing existing fields.
        for member in sequence.fields:
            _ = self._members.pop(member.name, None)
            if member.name in self.fields:
                self.fields.remove(member)
        return self

    __iadd__ = __add__  # pyright: ignore[reportUnannotatedClassAttribute]
    __isub__ = __sub__  # pyright: ignore[reportUnannotatedClassAttribute]

    def __type__(self) -> type:
        return dict

    def has_option(self, option: _OptionLike[Any]) -> bool:
        """
        Check if the struct has a specific option.

        :param option: The option to check.
        :return: True if the struct has the specified option, else False.
        """
        return option in self.options

    def _included(self, name: str, default: object, annotation: _AnnotationT) -> bool:
        """
        Check if a field with the given name should be included.

        :param name: The name of the field.
        :param default: The default value of the field.
        :return: True if the field should be included, else False.
        """
        if self.has_option(S_DISCARD_UNNAMED):
            if re.match(r"^_[0-9]*$", name):
                return False

        if self.has_option(S_DISCARD_CONST):
            if default != INVALID_DEFAULT:
                return False

        return True

    def _set_default(self, name: str, value: object) -> None:
        pass

    def _process_default(
        self, name: str, annotation: _AnnotationT, had_default: bool = False
    ) -> Any:
        default: Any = getattr(self.model, name, INVALID_DEFAULT)
        # constant values that are not in the form of fields, structs or types should
        # be wrapped into constant values. For more information, see _process_field
        if isinstance(annotation, Field):
            if annotation.has_condition():
                # Conditional fields always get a default value
                default = None
            annotation = annotation.struct

        match annotation:
            case bytes() | str():
                default = annotation
            # Make it possible to define custom constants
            case Const():
                default = annotation.value

        if self.is_union:
            # Unions will get none as default value for all fields
            default = None

        if default != INVALID_DEFAULT:
            self._set_default(name, default)
        return default

    def _replace_type(self, name: str, type_: type) -> None:
        pass

    def _remove_from_model(self, name: str) -> None:
        pass

    def _process_model(self) -> None:
        """
        Process all fields in the model.
        """
        removables: list[str] = []
        annotations = self._prepare_fields()
        had_default = False
        for name, annotation in annotations.items():
            annotated_type: type | None = None
            extra_options: Iterable[_ExtraOptionT] = []
            if get_origin(annotation) is Annotated:
                annotated_type, annotation, *extra_options = get_args(annotation)

            if Action.is_action(annotation):
                self.add_action(annotation)
                removables.append(name)
                continue

            # Process each field and its annotation. In addition, fields with a name in
            # the form of '_[0-9]*' will be removed (if enabled)
            default = self._process_default(name, annotation, had_default)
            if default != INVALID_DEFAULT:
                had_default = True
            is_included = self._included(name, default, annotation)
            if not is_included:
                removables.append(name)

            field = self._process_field(name, annotation, default)
            # a small hack to support 3.10
            options = list(extra_options)
            if len(options) == 1 and isinstance(options[0], Iterable):
                # fmt: off
                options: list[_ExtraOptionT] = options[0]  # pyright: ignore[reportAssignmentType]

            for extra_option in options:
                match extra_option:
                    case _ArchLike():
                        field.arch = extra_option
                    case _EndianLike():
                        field.order = extra_option
                    case _OptionLike():
                        field.add_flag(extra_option)
                    case _:
                        raise ValidationError(
                            f"Could not add extra option: unsupported type ({type(extra_option)})"
                        )

            # we call add_field to safely add the created field
            self.add_field(name, field, is_included)
            if self.has_option(S_REPLACE_TYPES):
                # This way we re-annotate all fields in the current model
                self._replace_type(name, annotated_type or field.get_type())

        for name in removables:
            self._remove_from_model(name)

    def _prepare_fields(self) -> dict[str, _AnnotationT]:
        return self.model  # pyright: ignore[reportReturnType]

    def _process_annotation(
        self,
        annotation: _AnnotationT,
        default: object,  # REVISIT: unused
        order: _EndianLike | None,
        arch: _ArchLike | None,
    ) -> _StructLike:
        return registry.to_struct(annotation)

    def _process_field(self, name: str, annotation: object, default: object) -> Field:
        """
        Process a field in the model.

        :param name: The name of the field.
        :param annotation: The annotation of the field.
        :param default: The default value of the field.
        :return: The processed field.
        """
        field = None
        struct = None

        # The order and arch of the field can be overridden by the annotation
        # and should not get applied if this seq does not define it.
        order = self.order  #  or getattr(annotation, ATTR_BYTEORDER, None)
        arch = self.arch
        result = self._process_annotation(annotation, default, order=order, arch=arch)
        if isinstance(result, Field):
            field = result
        else:
            struct = result

        if struct is not None:
            field = Field(struct, default=default)

        if field is None:
            type_name = (
                self.model.__name__
                if isinstance(self.model, type)
                else f"<{self.__class__.__name__}>"
            )
            msg = (
                f"Field '{type_name}.{name}' could not be created, because "
                "the placed annotation does not have a corresponding handler:\n "
                f"type: {type(annotation)},\n annotation: {annotation!r}"
            )
            raise ValidationError(msg)
        field.default = default
        if not field.has_order():
            field.order = order
        if not field.has_arch():
            field.arch = arch
        field.flags.update(self.field_options)
        # field.flags.update({hash(x): x for x in self.field_options})
        return field

    def add_field(self, name: str, field: Field, included: bool = False) -> None:
        """
        Add a field to the struct.

        :param name: The name of the field.
        :param field: The field to add.
        :param included: True if the field should be included, else False.
        """
        self.fields.append(_Member(name, field, include=included))
        setattr(field, "__name__", name)
        if included:
            self._members[name] = field

    def add_action(self, action: _ActionLike) -> None:
        """
        Add an action to the struct.

        :param action: The action to add.
        """
        self.fields.append(_Member(None, action, is_action=True))

    def del_field(self, name: str, field: Field) -> None:
        """
        Remomves a field from this struct.

        :param name: The name of the field.
        :param field: The field to remove.
        """
        self._members.pop(name, None)
        self.fields.remove(field)  # REVISIT: invalid type here

    def get_members(self) -> dict[str, Field]:
        return self._members.copy()

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the struct.

        :param context: The context of the struct.
        :return: The size of the struct.
        """
        sizes: list[int] = []
        base_path: str = context[CTX_PATH]
        for member in self.fields:
            if member.is_action:
                continue
            field = member.field
            context[CTX_PATH] = f"{base_path}.{member.name}"
            sizes.append(field.__size__(context))

        return max(sizes) if self.is_union else sum(sizes)

    def unpack_one(self, context: _ContextLike) -> _SeqOT:
        # At first, we define the object context where the parsed values
        # will be stored
        factory = O_CONTEXT_FACTORY.value or Context
        init_data = factory()
        context[CTX_OBJECT] = factory(_parent=context)
        base_path: str = context[CTX_PATH]
        stream: _StreamType = context[CTX_STREAM]
        start = pos = max_size = 0
        if self.is_union:
            start: int = stream.tell()

        for member in self.fields:
            if member.is_action:
                if member.action_unpack:
                    member.action_unpack(context)
                continue

            if self.is_union:
                pos = stream.tell()

            # REVISIT: make this a real attribute
            name = member.name
            # The context path has to be changed accordingly
            context[CTX_PATH] = f"{base_path}.{name}"
            result = member.field.__unpack__(context)
            # the object's data shouldn't include removed fields
            context[CTX_OBJECT][name] = result
            if member.include:
                init_data[name] = result

            if self.is_union:
                # This union implementation will cover the max size
                max_size = max(max_size, stream.tell() - pos)
                stream.seek(start)

        obj = init_data
        if self.is_union:
            # Reset the stream position
            stream.seek(start + max_size)
        return obj  # pyright: ignore[reportReturnType]

    def __unpack__(self, context: _ContextLike) -> _SeqOT:
        """
        Unpack the struct from the stream.

        :param stream: The stream to unpack from.
        :param context: The context of the struct.
        :return: The unpacked object.
        """
        base_path: str = context[CTX_PATH]
        # REVISIT: the name 'this_context' is misleading here
        this_context = (O_CONTEXT_FACTORY.value or Context)(
            _root=context._root,
            _parent=context,
            _io=context[CTX_STREAM],
            _path=base_path,
        )
        # See __pack__ for more information
        field = context.get("_field")
        if field and context[CTX_SEQ]:
            return unpack_seq(
                context, self.unpack_one
            )  # pyright: ignore[reportReturnType]
        return self.unpack_one(this_context)

    def get_value(self, obj: _SeqIT, name: str, field: Field) -> Any | None:
        return obj.get(name, None)

    def pack_one(self, obj: _SeqIT, context: _ContextLike) -> None:
        max_size = 0
        union_field = None
        base_path: str = context[CTX_PATH]

        for member in self.fields:
            if member.is_action:
                if member.action_pack:
                    member.action_pack(context)
                continue

            # The name has to be set (important for current context)
            name = member.name
            field = member.field
            if self.is_union:
                # Union is only applicable for non-dynamic structs
                size: int = field.__size__(context)
                if size > max_size:
                    max_size = size
                    union_field = field
            else:
                # Default behaviour: let the field write its content to the stream.
                context[CTX_PATH] = f"{base_path}.{name}"
                if member.include:
                    value = self.get_value(obj, name, field)
                else:
                    # REVISIT: this line might not be necessary if const fields already
                    # use their internal value.
                    value = field.default if field.default != INVALID_DEFAULT else None
                field.__pack__(value, context)

        if self.is_union:
            if union_field is None:
                raise StructException(
                    "Invalid union config: no fields declared!", context
                )

            name = union_field.get_name()
            context[CTX_PATH] = ".".join([base_path, "<value>"])
            # REVISIT: are constant values allowed here? + name validation?
            value = self.get_value(obj, name, union_field)
            union_field.__pack__(value, context)

    def __pack__(self, obj: _SeqIT, context: _ContextLike) -> None:
        # As structs can be used in field definitions a field will call this struct
        # and could potentially be a sequence. Therefore, we have to check whether we
        # should unpack multiple objects.
        field = context.get(CTX_FIELD)
        if field and context[CTX_SEQ]:
            pack_seq(obj, context, self.pack_one)
        else:
            ctx = (O_CONTEXT_FACTORY.value or Context)(
                _root=context._root,
                _parent=context,
                _io=context[CTX_STREAM],
                _path=context[CTX_PATH],
                _obj=obj,
            )
            self.pack_one(obj, ctx)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(fields={list(self._members)})"

    @override
    def __str__(self) -> str:
        return self.__repr__()


# --- private sequence tyoe converter ---
@registry.TypeConverter(dict)
def _type_converter(
    annotation: _SeqModelT, kwargs: dict[str, Any]
) -> Sequence[_SeqModelT]:
    arch: _ArchLike | None = kwargs.pop("arch", None)
    order: _EndianLike | None = kwargs.pop("order", None)
    return Sequence(model=annotation, order=order, arch=arch)


registry.annotation_registry.insert(0, _type_converter)
