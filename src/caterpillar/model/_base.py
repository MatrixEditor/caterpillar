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

from typing import Optional, Self, Tuple
from typing import List, Dict, Any
from typing import Set, Iterable, Union


from caterpillar.abc import _StructLike, _ContextLike, _StreamType, _Action
from caterpillar.context import Context, CTX_PATH, CTX_OBJECT, CTX_STREAM, CTX_SEQ
from caterpillar.byteorder import (
    BYTEORDER_FIELD,
    ByteOrder,
    SysNative,
    Arch,
    system_arch,
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
from caterpillar.shared import ATTR_ACTION_PACK, ATTR_ACTION_UNPACK, Action
from caterpillar import registry


class Sequence(FieldMixin):
    """Default implementation for a sequence of fields.

    The native Python type mapped to this struct class is :code:`dict`. To convert
    a dictionary into a sequence, you can either use the contructor directly or apply
    the type converter for this class:

    >>> to_struct({'a': uint8})
    Sequence(fields=['a'])
    """

    model: Any
    """
    Specifies the target class/dictionary used as the base model.
    """

    # second value with action in tuple is reserved
    fields: List[Field | Tuple[_Action, None]]
    """A list of all fields defined in this struct.

    This attribute stores the fields in an *ordered* collection, whereby ordered
    means, relative to their initial class declaration position. These fields can
    be modified using ``add_field``, ``del_field`` or the operators ``+`` and
    ``-``.
    """

    order: Optional[ByteOrder]
    """
    Optional configuration value for the byte order of a field.__annotations__
    """

    arch: Optional[Arch]
    """
    Global architecture definition (will be inferred on all fields)
    """

    options: Set[Flag]
    """
    Additional options specifying what to include in the final class.
    """

    field_options: Set[Flag]
    """
    Global field flags that will be applied on all fields.
    """

    __slots__ = (
        "model",
        "fields",
        "order",
        "arch",
        "options",
        "field_options",
        "_member_map_",
        "is_union",
    )

    def __init__(
        self,
        model: Optional[Dict[str, Field]] = None,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        options: Iterable[Flag] | None = None,
        field_options: Iterable[Flag] | None = None,
    ) -> None:
        self.model = model
        self.arch = arch
        self.order = order or SysNative
        self.options = set(options or [])
        self.field_options = set(field_options or [])

        # these fields will be set or used while processing the model type
        self._member_map_: Dict[str, Field] = {}
        self.fields = []
        self.is_union = S_UNION in self.options
        # Process all fields in the model
        self._process_model()

    def __add__(self, sequence: "Sequence") -> Self:
        # We will try to import all fields from the given sequence
        for field in sequence.fields:
            if Action.is_action(field):
                self.add_action(field)
            else:
                name = field.__name__
                if name not in self._member_map_:
                    is_included = name and name in sequence._member_map_
                    self.add_field(name, field, is_included)
        return self

    def __sub__(self, sequence: "Sequence") -> Self:
        # By default, we are only removing existing fields.
        for field in sequence.fields:
            if isinstance(field, Field):
                name = field.__name__
                if field in self.fields or (name and name in self._member_map_):
                    self.del_field(name, field)
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

    def _included(self, name: str, default: Optional[Any], annotation: Any) -> bool:
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

    def _set_default(self, name: str, value: Any) -> None:
        pass

    def _process_default(self, name, annotation: Any, had_default=False) -> Any:
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

    def _prepare_fields(self) -> Dict[str, Any]:
        return self.model

    def _process_annotation(
        self, annotation: Any, default: Optional[Any], order: ByteOrder, arch: Arch
    ) -> Union[_StructLike, Field]:
        return registry.to_struct(annotation, arch=arch, order=order)

    def _process_field(
        self, name: str, annotation: Any, default: Optional[Any]
    ) -> Field:
        """
        Process a field in the model.

        :param name: The name of the field.
        :param annotation: The annotation of the field.
        :param default: The default value of the field.
        :return: The processed field.
        """
        field: Field = None
        struct: _StructLike = None

        order = getattr(annotation, BYTEORDER_FIELD, self.order or SysNative)
        arch = self.arch or system_arch
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
        return field

    def add_field(self, name: str, field: Field, included: bool = False) -> None:
        """
        Add a field to the struct.

        :param name: The name of the field.
        :param field: The field to add.
        :param included: True if the field should be included, else False.
        """
        self.fields.append(field)
        setattr(field, "__name__", name)
        if included:
            self._member_map_[name] = field

    def add_action(self, action: _Action) -> None:
        self.fields.append((action, None))

    def del_field(self, name: str, field: Field) -> None:
        """
        Remomves a field from this struct.

        :param name: The name of the field.
        :param field: The field to remove.
        """
        self._member_map_.pop(name, None)
        self.fields.remove(field)

    def get_members(self) -> Dict[str, Field]:
        return self._member_map_.copy()

    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the struct.

        :param context: The context of the struct.
        :return: The size of the struct.
        """
        sizes = []
        base_path = context[CTX_PATH]
        for field in self.fields:
            context[CTX_PATH] = f"{base_path}.{field.__name__}"
            sizes.append(field.__size__(context))

        return max(sizes) if self.is_union else sum(sizes)

    def unpack_one(self, context: _ContextLike) -> Optional[Any]:
        # At first, we define the object context where the parsed values
        # will be stored
        init_data: Dict[str, Any] = Context()
        context[CTX_OBJECT] = Context(_parent=context)

        base_path = context[CTX_PATH]
        if self.is_union:
            start = context[CTX_STREAM].tell()
            max_size = 0

        for field in self.fields:
            if field.__class__ is tuple:
                action, _ = field
                action = getattr(action, ATTR_ACTION_UNPACK, None)
                if action:
                    action(context)
                continue

            if self.is_union:
                pos = context[CTX_STREAM].tell()

            # REVISIT: make this a real attribute
            name = field.__name__
            # The context path has to be changed accordingly
            context[CTX_PATH] = f"{base_path}.{name}"
            result = field.__unpack__(context)
            # the object's data shouldn't include removed fields
            context[CTX_OBJECT][name] = result
            if name in self._member_map_:
                init_data[name] = result

            if self.is_union:
                # This union implementation will cover the max size
                max_size = max(context[CTX_STREAM], stream.tell() - pos)
                context[CTX_STREAM].seek(start)

        obj = init_data
        if self.is_union:
            # Reset the stream position
            stream.seek(start + max_size)
        return obj

    def __unpack__(self, context: _ContextLike) -> Optional[Any]:
        """
        Unpack the struct from the stream.

        :param stream: The stream to unpack from.
        :param context: The context of the struct.
        :return: The unpacked object.
        """
        base_path = context[CTX_PATH]
        # REVISIT: the name 'this_context' is misleading here
        this_context = Context(
            _parent=context, _io=context[CTX_STREAM], _path=base_path
        )
        # See __pack__ for more information
        field: Optional[Field] = context.get("_field")
        if field and context[CTX_SEQ]:
            return unpack_seq(context, self.unpack_one)
        return self.unpack_one(this_context)

    def get_value(self, obj: Any, name: str, field: Field) -> Optional[Any]:
        return obj.get(name, None)

    def pack_one(self, obj: Dict[str, Any], context: _ContextLike) -> None:
        max_size = 0
        union_field: Optional[_StructLike] = None
        base_path: str = context[CTX_PATH]

        for field in self.fields:
            if field.__class__ is tuple:
                action, _ = field
                action = getattr(action, ATTR_ACTION_PACK, None)
                if action:
                    action(context)
                continue
            # The name has to be set (important for current context)
            name = field.__name__
            if self.is_union:
                # Union is only applicable for non-dynamic structs
                size: int = field.__size__(context)
                if size > max_size:
                    max_size = size
                    union_field = field
            else:
                # Default behaviour: let the field write its content to the stream.
                context[CTX_PATH] = f"{base_path}.{name}"
                if name in self._member_map_:
                    value = self.get_value(obj, name, field)
                else:
                    # REVISIT: this line might not be necessary if const fields alredy
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

    def __pack__(self, obj: Any, context: _ContextLike) -> None:
        # As structs can be used in field definitions a field will call this struct
        # and could potentially be a sequence. Therefore, we have to check whether we
        # should unpack multiple objects.
        field: Optional[Field] = context.get("_field")
        if field and context[CTX_SEQ]:
            pack_seq(obj, context, self.pack_one)
        else:
            ctx = Context(
                _parent=context,
                _io=context[CTX_STREAM],
                _path=context[CTX_PATH],
                _obj=obj,
            )
            self.pack_one(obj, ctx)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(fields={list(self._member_map_)})"

    def __str__(self) -> str:
        return self.__repr__()


# --- private sequence tyoe converter ---
@registry.TypeConverter(dict)
def _type_converter(annotation: Any, kwargs: dict) -> _StructLike:
    arch = kwargs.pop("arch", None)
    order = kwargs.pop("order", None)
    return Sequence(model=annotation, order=order, arch=arch)


registry.annotation_registry.insert(0, _type_converter)
