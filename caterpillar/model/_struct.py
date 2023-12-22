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
import inspect

from tempfile import TemporaryFile
from io import BytesIO, IOBase
from typing import Optional, Union
from typing import Dict, Any, Iterable
from collections import OrderedDict
from dataclasses import dataclass
from shutil import copyfileobj

from caterpillar.abc import (
    _StructLike,
    _StreamType,
    _ContainsStruct,
    _ContextLambda,
    _ContextLike,
    hasstruct,
    getstruct,
    STRUCT_FIELD,
)
from caterpillar.context import Context
from caterpillar.byteorder import (
    SysNative,
    ByteOrder,
    Arch,
    BYTEORDER_FIELD,
    get_system_arch,
)
from caterpillar.exception import ValidationError
from caterpillar.options import (
    S_EVAL_ANNOTATIONS,
    S_REPLACE_TYPES,
    S_UNION,
    Flag,
    GLOBAL_STRUCT_OPTIONS,
    GLOBAL_UNION_OPTIONS,
)
from caterpillar.fields import Field, INVALID_DEFAULT, ConstString, ConstBytes

from ._base import Sequence


@dataclass(init=False)
class Struct(Sequence):
    """
    Represents a structured data model for serialization and deserialization.

    :param model: The target class used as the base model.
    :param order: Optional byte order for the fields in the structure.
    :param arch: Global architecture definition (will be inferred on all fields).
    :param options: Additional options specifying what to include in the final class.
    """

    model: type
    """
    Specifies the target class used as the base model.
    """

    # _member_map_: Dict[str, Field]
    # An internal field that maps the field names of all class attributes to their
    # corresponding struct fields.

    def __init__(
        self,
        model: type,
        order: Optional[ByteOrder] = None,
        arch: Optional[Arch] = None,
        options: Iterable[Flag] = None,
        field_options: Iterable[Flag] = None,
    ) -> None:
        self.model = model
        super().__init__(
            order=order, arch=arch, options=options, field_options=field_options
        )
        # Add additional options based on the struct's type
        self.options.update(
            GLOBAL_UNION_OPTIONS if self.is_union() else GLOBAL_STRUCT_OPTIONS
        )
        # Process all fields in the model
        self._process_model()
        self.model = dataclass(self.model, kw_only=True)
        setattr(self.model, STRUCT_FIELD, self)
        setattr(self.model, "__class_getitem__", lambda dim: Field(self, amount=dim))

    def _process_model(self) -> None:
        """
        Process all fields in the model.
        """
        eval_str = self.has_option(S_EVAL_ANNOTATIONS)
        # The why is desribed in detail here: https://docs.python.org/3/howto/annotations.html
        annotations = inspect.get_annotations(self.model, eval_str=eval_str)

        removables = []
        for name, annotation in annotations.items():
            # Process each field and its annotation. In addition, fields with a name in
            # the form of '_[0-9]*' will be removed (if enabled)
            default = getattr(self.model, name, INVALID_DEFAULT)
            # constant values that are not in the form of fields, structs or types should
            # be wrapped into constant values. For more information, see _process_field
            if isinstance(annotation, bytes):
                default = annotation
                setattr(self.model, name, default)

            is_included = self._included(name, default, annotation)
            if not is_included:
                removables.append(name)

            field = self._process_field(name, annotation, default)
            # we call add_field to safely add the created field
            self.add_field(name, field, is_included)
            if self.has_option(S_REPLACE_TYPES):
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
        # TODO: register factories
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
        elif isinstance(annotation, str):
            struct = ConstString(annotation)
        elif isinstance(annotation, bytes):
            struct = ConstBytes(annotation)
        elif isinstance(annotation, _ContextLambda):
            struct = annotation

        if struct is not None:
            field = Field(struct, order, arch=arch, default=default)

        if field is None:
            raise ValidationError(
                f"Field {name!r} could not be created: {annotation!r}"
            )

        field.default = default
        field.order = self.order or field.order
        field.arch = self.arch or field.arch
        field.flags.update(self.field_options)
        return field

    def unpack_one(self, stream: _StreamType, context: _ContextLike) -> Optional[Any]:
        init_data = super().unpack_one(stream, context)
        return self.model(**init_data)

    def get_value(self, obj: Any, name: str, field: Field) -> Optional[Any]:
        return getattr(obj, name, None)


def _make_struct(
    cls: type,
    options: Iterable[Flag],
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Iterable[Flag] = None,
) -> type:
    """
    Helper function to create a Struct class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Struct class.
    """
    _ = Struct(
        cls, order=order, arch=arch, options=options, field_options=field_options
    )
    return cls


def struct(
    cls: type = None,
    /,
    *,
    options: Iterable[Flag] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Iterable[Flag] = None,
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
        return _make_struct(
            cls, options=options, order=order, arch=arch, field_options=field_options
        )

    if cls is not None:
        return _make_struct(
            cls, options=options, order=order, arch=arch, field_options=field_options
        )

    return wrap


def union(
    cls: type = None,
    /,
    *,
    options: Iterable[Flag] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Iterable[Flag] = None,
):
    """
    Decorator to create a Union class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Union class or a wrapper function if cls is not provided.
    """
    options = set(list(options or []) + [S_UNION])

    def wrap(cls):
        return _make_struct(
            cls, options=options, order=order, arch=arch, field_options=field_options
        )

    if cls is not None:
        return _make_struct(
            cls, options=options, order=order, arch=arch, field_options=field_options
        )

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
    use_tempfile: bool = False,
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

    offsets: Dict[int, memoryview] = OrderedDict()
    context = Context(_parent=None, _path="<root>", _pos=0, _offsets=offsets, **kwds)
    if struct is None:
        struct = getstruct(obj)

    start = 0
    if use_tempfile:
        # NOTE: this implementation is exprimental - use this option with caution.
        with TemporaryFile() as stream:
            context._io = stream
            struct.__pack__(obj, stream, context)

            for offset, value in offsets.items():
                stream.seek(start)
                buffer.write(stream.read(offset - start))
                buffer.write(value)
                start = offset
            else:
                stream.seek(0)
                copyfileobj(stream, buffer)

    else:
        # Default implementation: We use an in-memory buffer to store all packed
        # elements and then apply all offset-packed objects.
        stream = BytesIO()
        context._io = stream
        struct.__pack__(obj, stream, context)

        content = stream.getbuffer()
        for offset, value in offsets.items():
            buffer.write(content[start:offset])
            buffer.write(value)
            start = offset
        else:
            buffer.write(content)


def pack_file(
    obj: Union[Any, _ContainsStruct],
    filename: str,
    struct: Optional[_StructLike] = None,
    use_tempfile: bool = False,
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
        pack_into(obj, fp, struct, use_tempfile, **kwds)


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
