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
import re

from typing import Self, override

from caterpillar.context import (
    CTX_FIELD,
    CTX_PATH,
    CTX_OBJECT,
    CTX_STREAM,
    CTX_SEQ,
    O_CONTEXT_FACTORY,
)
from caterpillar.byteorder import (
    ByteOrder,
    Arch,
)
from caterpillar.exception import StructException, ValidationError
from caterpillar.options import (
    S_DISCARD_CONST,
    S_DISCARD_UNNAMED,
    S_UNION,
    S_REPLACE_TYPES,
    Flag,
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
    ATTR_BYTEORDER,
)
from caterpillar import registry


class _Member:
    def __init__(self, name, field, include=False, is_action=False):
        self.name = name
        self.field = field
        self.include = include
        self.is_action = is_action
        self.action_unpack = getattr(field, ATTR_ACTION_UNPACK, None)
        self.action_pack = getattr(field, ATTR_ACTION_PACK, None)

    def __repr__(self):
        if self.is_action:
            return f"Action({self.field})"

        return f"Member(name={self.name}, field={self.field}, include={self.include})"

    @override
    def __eq__(self, value: object, /) -> bool:
        return self.field == value or value == self.name


class Sequence(FieldMixin):
    """Default implementation for a sequence of fields.

    The native Python type mapped to this struct class is :code:`dict`. To convert
    a dictionary into a sequence, you can either use the contructor directly or apply
    the type converter for this class:

    >>> to_struct({'a': uint8})
    Sequence(fields=['a'])
    """

    __slots__ = (
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
        model,
        order=None,
        arch=None,
        options=None,
        field_options=None,
    ) -> None:
        self.model = model
        self.arch = arch
        self.order = order
        self.options = set(options or [])
        self.field_options = set(field_options or [])

        # these fields will be set or used while processing the model type
        self._members = {}
        self.fields = []
        self.is_union = S_UNION in self.options
        # Process all fields in the model
        self._process_model()

    def __add__(self, sequence: "Sequence") -> Self:
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
            self._members.pop(member.name, None)
            if member.name in self.fields:
                self.fields.remove(member)
        return self

    __iadd__ = __add__
    __isub__ = __sub__

    def __type__(self) -> type:
        return dict

    def has_option(self, option: Flag) -> bool:
        """
        Check if the struct has a specific option.

        :param option: The option to check.
        :return: True if the struct has the specified option, else False.
        """
        return option in self.options

    def _included(self, name: str, default, annotation) -> bool:
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

    def _set_default(self, name: str, value) -> None:
        pass

    def _process_default(self, name, annotation, had_default=False):
        default = getattr(self.model, name, INVALID_DEFAULT)
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
        removables = []
        annotations = self._prepare_fields()
        had_default = False
        for name, annotation in annotations.items():
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
            # we call add_field to safely add the created field
            self.add_field(name, field, is_included)
            if self.has_option(S_REPLACE_TYPES):
                # This way we re-annotate all fields in the current model
                self._replace_type(name, field.get_type())

        for name in removables:
            self._remove_from_model(name)

    def _prepare_fields(self):
        return self.model

    def _process_annotation(self, annotation, default, order: ByteOrder, arch: Arch):
        return registry.to_struct(annotation, arch=arch, order=order)

    def _process_field(self, name: str, annotation, default) -> Field:
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
        order = getattr(annotation, ATTR_BYTEORDER, self.order)
        arch = self.arch
        result = self._process_annotation(annotation, default, order, arch)
        if isinstance(result, Field):
            field = result
        else:
            struct = result

        if struct is not None:
            field = Field(struct, order, arch=arch, default=default)

        if field is None:
            msg = (
                f"Field '{self.model.__name__}.{name}' could not be created, because "
                "the placed annotation does not have a corresponding handler:\n "
                f"type: {type(annotation)},\n annotation: {annotation!r}"
            )
            raise ValidationError(msg)
        field.default = default
        field.order = self.order or field.order
        field.arch = self.arch or field.arch
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

    def add_action(self, action) -> None:
        """
        Add an action to the struct.

        :param action: The action to add.
        """
        self.fields.append(_Member(None, action, is_action=True))

    def del_field(self, name: str, field) -> None:
        """
        Remomves a field from this struct.

        :param name: The name of the field.
        :param field: The field to remove.
        """
        self._members.pop(name, None)
        self.fields.remove(field)

    def get_members(self):
        return self._members.copy()

    def __size__(self, context) -> int:
        """
        Get the size of the struct.

        :param context: The context of the struct.
        :return: The size of the struct.
        """
        sizes = []
        base_path = context[CTX_PATH]
        for member in self.fields:
            if member.is_action:
                continue
            field = member.field
            context[CTX_PATH] = f"{base_path}.{member.name}"
            sizes.append(field.__size__(context))

        return max(sizes) if self.is_union else sum(sizes)

    def unpack_one(self, context):
        # At first, we define the object context where the parsed values
        # will be stored
        init_data = O_CONTEXT_FACTORY.value()
        context[CTX_OBJECT] = O_CONTEXT_FACTORY.value(_parent=context)

        base_path = context[CTX_PATH]
        if self.is_union:
            stream = context[CTX_STREAM]
            start = stream.tell()
            max_size = 0

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
        return obj

    def __unpack__(self, context):
        """
        Unpack the struct from the stream.

        :param stream: The stream to unpack from.
        :param context: The context of the struct.
        :return: The unpacked object.
        """
        base_path = context[CTX_PATH]
        # REVISIT: the name 'this_context' is misleading here
        this_context = O_CONTEXT_FACTORY.value(
            _root=context._root,
            _parent=context,
            _io=context[CTX_STREAM],
            _path=base_path,
        )
        # See __pack__ for more information
        field = context.get("_field")
        if field and context[CTX_SEQ]:
            return unpack_seq(context, self.unpack_one)
        return self.unpack_one(this_context)

    def get_value(self, obj, name: str, field: Field):
        return obj.get(name, None)

    def pack_one(self, obj, context) -> None:
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

            name = union_field.__name__
            context[CTX_PATH] = ".".join([base_path, "<value>"])
            # REVISIT: are constant values allowed here? + name validation?
            value = self.get_value(obj, name, union_field)
            union_field.__pack__(value, context)

    def __pack__(self, obj, context) -> None:
        # As structs can be used in field definitions a field will call this struct
        # and could potentially be a sequence. Therefore, we have to check whether we
        # should unpack multiple objects.
        field = context.get(CTX_FIELD)
        if field and context[CTX_SEQ]:
            pack_seq(obj, context, self.pack_one)
        else:
            ctx = O_CONTEXT_FACTORY.value(
                _root=context._root,
                _parent=context,
                _io=context[CTX_STREAM],
                _path=context[CTX_PATH],
                _obj=obj,
            )
            self.pack_one(obj, ctx)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(fields={list(self._members)})"

    def __str__(self) -> str:
        return self.__repr__()


# --- private sequence tyoe converter ---
@registry.TypeConverter(dict)
def _type_converter(annotation, kwargs: dict):
    arch = kwargs.pop("arch", None)
    order = kwargs.pop("order", None)
    return Sequence(model=annotation, order=order, arch=arch)


registry.annotation_registry.insert(0, _type_converter)
