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

from caterpillar.abc import getstruct, hasstruct, STRUCT_FIELD
from caterpillar.abc import _StructLike, _StreamType
from caterpillar.abc import _ContainsStruct, _ContextLike, _SupportsSize
from caterpillar.context import Context, CTX_STREAM
from caterpillar.byteorder import ByteOrder, Arch
from caterpillar.options import (
    S_EVAL_ANNOTATIONS,
    S_UNION,
    Flag,
    GLOBAL_STRUCT_OPTIONS,
    GLOBAL_UNION_OPTIONS,
)
from caterpillar.fields import Field
from ._base import Sequence


class Struct(Sequence):
    """
    Represents a structured data model for serialization and deserialization.

    :param model: The target class used as the base model.
    :param order: Optional byte order for the fields in the structure.
    :param arch: Global architecture definition (will be inferred on all fields).
    :param options: Additional options specifying what to include in the final class.
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
        options = options or set()
        options.update(
            GLOBAL_UNION_OPTIONS if S_UNION in options else GLOBAL_STRUCT_OPTIONS
        )
        super().__init__(
            model=model,
            order=order,
            arch=arch,
            options=options,
            field_options=field_options,
        )
        # Add additional options based on the struct's type
        self.model = dataclass(self.model, kw_only=True)
        setattr(self.model, STRUCT_FIELD, self)
        setattr(self.model, "__class_getitem__", lambda dim: Field(self, amount=dim))

    def __type__(self) -> type:
        return self.model

    def _prepare_fields(self) -> Dict[str, Any]:
        # We will inspect all base classes in reverse order and selectively
        # utilize classes that store a struct instance. Beginning at position
        # -1, concluding at 0, and using a step size of -1:
        for candidate in self.model.__mro__[-1:0:-1]:
            if hasstruct(candidate):
                # Importing all fields instead of the entire struct.
                # The default behavior on importing structs is implemented
                # by the Sequence class.
                struct = getstruct(candidate)
                self += struct

        eval_str = self.has_option(S_EVAL_ANNOTATIONS)
        # The why is described in detail here: https://docs.python.org/3/howto/annotations.html
        return inspect.get_annotations(self.model, eval_str=eval_str)

    def _set_default(self, name: str, value: Any) -> None:
        setattr(self.model, name, value)

    def _replace_type(self, name: str, type_: type) -> None:
        self.model.__annotations__[name] = type_

    def _remove_from_model(self, name: str) -> None:
        self.model.__annotations__.pop(name)

    def unpack_one(self, context: _ContextLike) -> Optional[Any]:
        return self.model(**super().unpack_one(context))

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
    elif hasstruct(struct):
        struct = getstruct(struct)

    start = 0
    if use_tempfile:
        # NOTE: this implementation is exprimental - use this option with caution.
        with TemporaryFile() as stream:
            context[CTX_STREAM] = stream
            struct.__pack__(obj, context)

            for offset, value in offsets.items():
                stream.seek(start)
                buffer.write(stream.read(offset - start))
                buffer.write(value)
                start = offset
            if len(offsets) == 0:
                stream.seek(0)
                copyfileobj(stream, buffer)

    else:
        # Default implementation: We use an in-memory buffer to store all packed
        # elements and then apply all offset-packed objects.
        stream = BytesIO()
        context[CTX_STREAM] = stream
        struct.__pack__(obj, context)

        content = stream.getbuffer()
        for offset, value in offsets.items():
            buffer.write(content[start:offset])
            buffer.write(value)
            start = offset
        if len(offsets) == 0:
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

    return struct.__unpack__(context)


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


def sizeof(obj: Union[_StructLike, _ContainsStruct, _SupportsSize], **kwds) -> int:
    context = Context(_parent=None, _path="<root>", **kwds)
    struct_ = obj
    if hasstruct(struct_):
        struct_ = getstruct(struct_)
    return struct_.__size__(context)
