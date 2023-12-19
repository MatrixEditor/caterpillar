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

import inspect
import re

from io import BytesIO, IOBase
from typing import Optional, Union
from typing import List, Dict, Any
from typing import Set, Iterable
from dataclasses import dataclass

from caterpillar.abc import _StructLike, _ContextLike, _StreamType, _ContainsStruct
from caterpillar.context import Context
from caterpillar.byteorder import (
    SysNative,
    ByteOrder,
    Arch,
    BYTEORDER_FIELD,
    get_system_arch,
)
from caterpillar.exception import ValidationError

from caterpillar.fields import Field, Flag, INVALID_DEFAULT, ConstBytes, ConstString


STRUCT_FIELD = "__struct__"


def hasstruct(obj: Any) -> bool:
    """
    Check if the given object has a structure attribute.

    :param obj: The object to check.
    :return: True if the object has a structure attribute, else False.
    """
    return bool(getattr(obj, STRUCT_FIELD, None))


def getstruct(obj: Any) -> Struct:
    """
    Get the structure attribute of the given object.

    :param obj: The object to get the structure attribute from.
    :return: The structure attribute of the object.
    """
    return getattr(obj, STRUCT_FIELD)


DISCARD_UNNAMED = Flag("discard_unnamed")
DISCARD_CONST = Flag("discard_const")
UNION = Flag("union")
REPLACE_TYPES = Flag("replace_types")


@dataclass(init=False)
class Struct(_StructLike):
    """
    Represents a structured data model for serialization and deserialization.

    :param model: The target class used as the base model.
    :param order: Optional byte order for the fields in the structure.
    :param arch: Global architecture definition (will be inferred on all fields).
    :param options: Additional options specifying what to include in the final class.
    """

    fields: List[Field]
    """A list of all fields defined in this struct.

    This attribute stores the fields in an *ordered* collection, whereby ordered
    means, relative to their initial class declaration position. These fields can
    be modified using ``add_field``, ``del_field`` or the operators ``+`` and
    ``-``.
    """

    model: type
    """
    Specifies the target class used as the base model.
    """

    # _member_map_: Dict[str, Field]
    # An internal field that maps the field names of all class attributes to their
    # corresponding struct fields.

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

    def __init__(
        self,
        model: type,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        options: Iterable[Flag] = None,
    ) -> None:
        self.model = model
        self.arch = arch
        self.order = order
        self.options = set(options or [])

        # these fields will be set or used while processing the model type
        self._member_map_ = {}
        self.fields = []
        # Process all fields in the model
        self._process_model()
        self.model = dataclass(self.model, kw_only=True)
        setattr(self.model, STRUCT_FIELD, self)

    def is_union(self) -> bool:
        """
        Check if the struct is a union.

        :return: True if the struct is a union, else False.
        """
        return self.has_option(UNION)

    def has_option(self, option: Flag) -> bool:
        """
        Check if the struct has a specific option.

        :param option: The option to check.
        :return: True if the struct has the specified option, else False.
        """
        return option in self.options

    def _included(self, name: str, default: Optional[Any]) -> bool:
        """
        Check if a field with the given name should be included.

        :param name: The name of the field.
        :param default: The default value of the field.
        :return: True if the field should be included, else False.
        """
        if self.has_option(DISCARD_UNNAMED):
            if re.match(r"^_[0-9]*$", name):
                return False

        if self.has_option(DISCARD_CONST):
            if default != INVALID_DEFAULT:
                return False

        return True

    def _process_model(self) -> None:
        """
        Process all fields in the model.
        """
        annotations = inspect.get_annotations(self.model)
        removables = []

        for name, annotation in annotations.items():
            # Process each field and its annotation. In addition, fields with a name in
            # the form of '_[0-9]*' will be removed (if enabled)
            default = getattr(self.model, name, INVALID_DEFAULT)
            # constant values that are not in the form of fields, structs or types should
            # be wrapped into constant values. For more information, see _process_field
            if isinstance(annotation, (int, str, bytes)):
                default = annotation
                setattr(self.model, name, default)

            is_included = self._included(name, default)
            if not is_included:
                removables.append(name)

            field = self._process_field(name, annotation, default)
            # we call add_field to safely add the created field
            self.add_field(name, field, is_included)
            if self.has_option(REPLACE_TYPES):
                # This way we re-annotate all fields in the current model
                self.model.__annotations__[name] = field.get_type()

        for name in removables:
            self.model.__annotations__.pop(name)

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
        arch = self.arch or get_system_arch()

        if isinstance(annotation, Field):
            field = annotation
        elif isinstance(annotation, _StructLike):
            # As Field is a direct subclass of _StructLike, we have to put this check
            # below this one.
            field = Field(annotation, order, arch=arch, default=default)
        elif isinstance(annotation, type):
            # types should be handled separately
            struct: _StructLike = None
            if hasstruct(annotation):
                struct = getstruct(annotation)
            else:
                struct = Struct(annotation, order=self.order, arch=self.arch)
            # TODO: handle ENUM types
        elif isinstance(annotation, str):
            struct = ConstString(annotation)
        elif isinstance(annotation, bytes):
            struct = ConstBytes(annotation)

        if struct is not None:
            field = Field(struct, order, arch=arch, default=default)

        if field is None:
            raise ValidationError(
                f"Field {name!r} could not be created: {str(annotation)!r}"
            )

        field.default = default
        field.order = self.order or field.order
        field.arch = self.arch or field.arch
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

    # I/O operations
    def __size__(self, context: _ContextLike) -> int:
        """
        Get the size of the struct.

        :param context: The context of the struct.
        :return: The size of the struct.
        """
        sizes = []
        base_path = context._path
        for field in self.fields:
            context._path = ".".join([base_path, field.get_name()])
            sizes.append(field.__size__(context))

        return max(sizes) if self.is_union() else sum(sizes)

    def __unpack__(self, stream: _StreamType, context: _ContextLike) -> Optional[Any]:
        """
        Unpack the struct from the stream.

        :param stream: The stream to unpack from.
        :param context: The context of the struct.
        :return: The unpacked object.
        """
        init_data: Dict[str, Any] = {}
        base_path = context._path
        this_context = Context(_parent=context, _io=stream, _path=base_path)
        start = stream.tell()
        max_size = 0

        for field in self.fields:
            pos = stream.tell()
            name = field.get_name()
            # The context path has to be changed accordingly
            this_context._path = ".".join([base_path, name])
            result = field.__unpack__(stream, this_context)
            context[name] = result
            # the object's data shouldn't include removed fields
            if name in self._member_map_:
                init_data[name] = result

            if self.is_union():
                # This union implementation will cover the max size
                max_size = max(max_size, stream.tell() - pos)
                stream.seek(start)

        # As referenced above, we can simply pass all fields here, because we've eliminated
        # all default values to enable required field definitions AFTER optional fields with
        # default values have been defined.
        obj = self.model(**init_data)
        if self.is_union():
            # Reset the stream position
            stream.seek(start + max_size)
        return obj

    def __pack__(self, obj: Any, stream: _StreamType, context: _ContextLike) -> None:
        # REVISIT: code cleanup
        base_path = context._path
        this_context = Context(_parent=context, _io=stream, _path=base_path)
        max_size = 0

        if not self.is_union():
            for field in self.fields:
                name = getattr(field, "__name__")
                this_context._path = ".".join([base_path, name])
                value = getattr(obj, name, None) if name in self._member_map_ else []
                field.__pack__(value, stream, this_context)

        else:
            # REVISIT: This is time consuming, we should cache the member's sise
            fields = {
                f.__size__(this_context): (f, n) for n, f in self._member_map_.items()
            }
            max_size = max(fields)
            field, name = fields[max_size]
            this_context._path = ".".join([base_path, name])
            field.__pack__(getattr(obj, name), stream, this_context)


def _make_struct(
    cls: type,
    options: Iterable[Flag],
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
) -> type:
    """
    Helper function to create a Struct class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Struct class.
    """
    _ = Struct(cls, order=order, arch=arch, options=options)
    return cls


def struct(
    cls: type = None,
    /,
    *,
    options: Iterable[Flag] = (),
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
):
    """
    Decorator to create a Struct class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Struct class or a wrapper function if cls is not provided.
    """

    def wrap(cls):
        return _make_struct(cls, options=options, order=order, arch=arch)

    if cls is not None:
        return _make_struct(cls, options=options, order=order, arch=arch)

    return wrap


def union(
    cls: type = None,
    /,
    *,
    options: Iterable[Flag] = (),
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
):
    """
    Decorator to create a Union class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Union class or a wrapper function if cls is not provided.
    """
    options = set(list(options) + [UNION])

    def wrap(cls):
        return _make_struct(cls, options=options, order=order, arch=arch)

    if cls is not None:
        return _make_struct(cls, options=options, order=order, arch=arch)

    return wrap


def pack(
    obj: Union[Any, _ContainsStruct],
    struct: Optional[_StructLike] = None,
    **kwds,
) -> bytes:
    """
    Pack an object into a bytes buffer using the specified struct.

    :param obj: The object to pack.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: The packed bytes.
    """
    buffer = BytesIO()
    pack_into(obj, buffer, struct, **kwds)
    return buffer.getvalue()


def pack_into(
    obj: Union[Any, _ContainsStruct],
    buffer: _StreamType,
    struct: Optional[_StructLike] = None,
    **kwds,
) -> None:
    """
    Pack an object into the specified buffer using the specified struct.

    :param obj: The object to pack.
    :param buffer: The buffer to pack the object into.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: None
    """
    context = Context(_parent=None, _path="<root>", _io=buffer, _pos=0, **kwds)
    if struct is None:
        struct = getstruct(obj)
    struct.__pack__(obj, buffer, context)


def pack_file(
    obj: Union[Any, _ContainsStruct],
    filename: str,
    struct: Optional[_StructLike] = None,
    **kwds,
) -> None:
    """
    Pack an object into a file using the specified struct.

    :param obj: The object to pack.
    :param filename: The name of the file to write to.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: None
    """
    with open(filename, "wb") as fp:
        pack_into(obj, fp, struct, **kwds)


def unpack(
    struct: Union[_StructLike, _ContainsStruct],
    buffer: Union[bytes, _StreamType],
    **kwds,
) -> Any:
    """
    Unpack an object from a bytes buffer or stream using the specified struct.

    :param struct: The struct to use for unpacking.
    :param buffer: The bytes buffer or stream to unpack from.
    :param kwds: Additional keyword arguments to pass to the unpack function.

    :return: The unpacked object.
    """
    # prepare the data stream
    stream = buffer if isinstance(buffer, IOBase) else BytesIO(buffer)
    context = Context(_path="<root>", _parent=None, _io=stream, **kwds, _pos=0)
    if hasstruct(struct):
        struct = getstruct(struct)

    return struct.__unpack__(stream, context)


def unpack_file(
    struct: Union[_StructLike, _ContainsStruct],
    filename: str,
    **kwds,
) -> Any:
    """
    Unpack an object from a file using the specified struct.

    :param struct: The struct to use for unpacking.
    :param filename: The name of the file to read from.
    :param kwds: Additional keyword arguments to pass to the unpack function.

    :return: The unpacked object.
    """
    with open(filename, "rb") as fp:
        return unpack(struct, fp, **kwds)
