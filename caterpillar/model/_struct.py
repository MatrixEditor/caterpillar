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
from typing import Optional, Union, Callable
from typing import Dict, Any, Iterable
from collections import OrderedDict
from dataclasses import dataclass
from shutil import copyfileobj

from caterpillar.abc import getstruct, hasstruct, STRUCT_FIELD
from caterpillar.abc import _StructLike, _StreamType, _SupportsUnpack
from caterpillar.abc import _ContainsStruct, _ContextLike, _SupportsSize
from caterpillar.context import Context, CTX_STREAM
from caterpillar.byteorder import ByteOrder, Arch
from caterpillar.options import (
    S_EVAL_ANNOTATIONS,
    S_UNION,
    S_ADD_BYTES,
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
        kw_only: bool = False,
        hook_cls: Optional[type] = None,
    ) -> None:
        self.kw_only = kw_only
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
        self.model = dataclass(self.model, kw_only=self.kw_only)
        setattr(self.model, STRUCT_FIELD, self)
        setattr(self.model, "__class_getitem__", lambda dim: Field(self, amount=dim))
        if self.is_union:
            # install a hook
            self._union_hook = (hook_cls or UnionHook)(self)
            setattr(self.model, "__init__", _union_init(self._union_hook))
            setattr(self.model, "__setattr__", _union_setattr(self._union_hook))
        if self.has_option(S_ADD_BYTES):
            setattr(self.model, "__bytes__", _struct_bytes)

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
                self += getstruct(candidate)

        eval_str = self.has_option(S_EVAL_ANNOTATIONS)
        # The why is described in detail here: https://docs.python.org/3/howto/annotations.html
        return inspect.get_annotations(self.model, eval_str=eval_str)

    def _set_default(self, name: str, value: Any) -> None:
        setattr(self.model, name, value)
        if not self.kw_only:
            self.kw_only = True

    def _replace_type(self, name: str, type_: type) -> None:
        self.model.__annotations__[name] = type_

    def _remove_from_model(self, name: str) -> None:
        self.model.__annotations__.pop(name)

    def unpack_one(self, context: _ContextLike) -> Optional[Any]:
        return self.model(**super().unpack_one(context))

    def get_value(self, obj: Any, name: str, field: Field) -> Optional[Any]:
        return getattr(obj, name, None)


def _struct_bytes(model: Struct) -> Callable:
    def to_bytes(self) -> bytes:
        return pack(self, model)

    return to_bytes


def _make_struct(
    cls: type,
    options: Iterable[Flag] = None,
    order: Optional[ByteOrder] = None,
    arch: Optional[Arch] = None,
    field_options: Iterable[Flag] = None,
    kw_only: bool = False,
    hook_cls: Optional[type] = None,
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
        cls,
        order=order,
        arch=arch,
        options=options,
        field_options=field_options,
        kw_only=kw_only,
        hook_cls=hook_cls,
    )
    return cls


def struct(cls: type = None, /, **kwds):
    """
    Decorator to create a Struct class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Struct class or a wrapper function if cls is not provided.
    """

    def wrap(cls):
        return _make_struct(cls, **kwds)

    if cls is not None:
        return _make_struct(cls, **kwds)

    return wrap


class UnionHook:
    """Implementation of a hook to simulate union types.

    It will hook two methods of the target model type: :code:`__init__` and
    :code:`__setattr__`. Because the constructor calls *setattr* for each
    attribute in the model, we have to intercept it before it gets called
    to set an internal status.

    Internally, these two methods will be translated into :meth:`~UnionHook.__model_init__`
    and :meth:`~UnionHook.__model_setattr__`. Therefore, any class that implements
    these two methods can be used as a union hook.
    """

    struct: Struct
    """The struct reference"""

    max_size: int
    """The static (cached) maximum size of the union"""

    def __init__(self, struct_: Struct) -> None:
        self.struct = struct_
        # Dynamic size is not allowed and will throw an error here
        self.max_size = sizeof(struct_)
        # These attributes are set by default
        self._processing_ = False
        self._model_init_ = struct_.model.__init__

    def __enter__(self) -> None:
        # shortcut for disabling permanent attribute refresh during
        # init and refresh phases
        self._processing_ = True

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # This variable MUST be reset afterward
        self._processing_ = False

    def __model_init__(self, obj: Any, *args, **kwargs) -> None:
        # since it is possible now, to specify non-kw_only constructors,
        # we have to capture both, args and kwargs
        with self:
            return self._model_init_(obj, *args, **kwargs)

    def __model_setattr__(self, obj: Any, key: str, new_value: Any) -> None:
        # The target attribute will alyaws be set
        object.__setattr__(obj, key, new_value)

        members: Dict[str, Field] = self.struct.get_members()
        if self._processing_ or key not in members:
            # Refresh can't be done if:
            #   1) the current instance is alredy being processed
            #   2) the member is not in the internal model
            return

        with self:
            # delegation into method allows for customisation
            self.refresh(obj, key, new_value, members)

    def refresh(
        self, obj: Any, key: str, new_value: Any, members: Dict[str, Field]
    ) -> None:
        # DEFAULT: retrieve the current field and temporarily pack its data
        field = members[key]
        data = pack(new_value, field)

        # Apply a padding to the retrieved data
        stream = BytesIO(data + b"\0" * (self.max_size - len(data)))
        for name, field in members.items():
            # this field shouldn't be updated as it already was
            if name == key:
                continue

            # we can simply use setattr here
            object.__setattr__(obj, name, unpack(field, stream))
            stream.seek(0)


def _union_init(hook: UnionHook) -> Callable:
    # wrapper function to capture the calling instance
    def init(self, *args, **kwargs) -> None:
        return hook.__model_init__(self, *args, **kwargs)

    return init


def _union_setattr(hook: UnionHook) -> Callable:
    # wrapper function to capture the calling instance
    def setattribute(self, key: str, value: Any) -> None:
        hook.__model_setattr__(self, key, value)

    return setattribute


def union(cls: type = None, /, *, options: Iterable[Flag] = None, **kwds):
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
        return _make_struct(cls, options=options, **kwds)

    if cls is not None:
        return _make_struct(cls, options=options, **kwds)

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
    struct: Union[_SupportsUnpack, _ContainsStruct],
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
    context = Context(
        _path="<root>", _parent=None, _io=stream, **kwds, _pos=0, _is_seq=False
    )
    if hasstruct(struct):
        struct = getstruct(struct)

    if not isinstance(struct, _SupportsUnpack):
        raise TypeError(f"{type(struct).__name__} is not a valid struct instance!")

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
