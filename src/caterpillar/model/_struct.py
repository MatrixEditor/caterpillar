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
# pyright: reportAny=false, reportExplicitAny=false, reportPrivateUsage=false
import inspect
import dataclasses as dc

from tempfile import TemporaryFile
from io import BytesIO, IOBase
from collections import OrderedDict
from collections.abc import Collection, Iterable
from shutil import copyfileobj
from typing import Any, Callable, Generic, Literal, ParamSpec, TypeVar
from types import TracebackType
from typing_extensions import (
    ClassVar,
    Self,
    dataclass_transform,
    override,
    overload,
    Buffer,
)

from caterpillar.byteorder import (
    O_DEFAULT_ARCH,
    O_DEFAULT_ENDIAN,
    LittleEndian,
    system_arch,
)
from caterpillar.shared import ATTR_PACK, getstruct, hasstruct, ATTR_STRUCT
from caterpillar.context import O_CONTEXT_FACTORY, CTX_STREAM, Context
from caterpillar.exception import DynamicSizeError, InvalidValueError
from caterpillar.options import (
    S_EVAL_ANNOTATIONS,
    S_UNION,
    S_ADD_BYTES,
    S_SLOTS,
    GLOBAL_STRUCT_OPTIONS,
    GLOBAL_UNION_OPTIONS,
)
from caterpillar.fields import Field, INVALID_DEFAULT
from caterpillar import registry
from caterpillar.shared import MODE_PACK, MODE_UNPACK
from caterpillar.abc import (
    _ContainsStruct,
    _OT,
    _IT,
    _SupportsPack,
    _StreamType,
    _SupportsUnpack,
    _ContextLike,
    _StructLike,
    _SupportsSize,
    _OptionLike,
    _EndianLike,
    _ArchLike,
    _LengthT,
)
from ._base import Sequence


_ModelT = TypeVar("_ModelT")


# REVISIT: remove dataclasses dependency
class Struct(Sequence[type[_ModelT], _ModelT, _ModelT]):
    """
    Represents a structured data model for serialization and deserialization.

    :param model: The target class used as the base model.
    :param order: Optional byte order for the fields in the structure.
    :param arch: Global architecture definition (will be inferred on all fields).
    :param options: Additional options specifying what to include in the final class.
    """

    #!! NOT PRESENT !!
    # _member_map_: dict
    # An internal field that maps the field names of all class attributes to their
    # corresponding struct fields.

    __slots__: tuple[str, ...] = ("kw_only", "_union_hook")

    def __init__(
        self,
        model: type[_ModelT],
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        options: Iterable[_OptionLike] | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        kw_only: bool = False,
        hook_cls: type["UnionHook[_ModelT]"] | None = None,
    ) -> None:
        self.kw_only: bool = kw_only
        options = set(options or [])
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
        setattr(self.model, ATTR_STRUCT, self)
        # Add additional options based on the struct's type
        slots = self.has_option(S_SLOTS)
        self.model: type[_ModelT] = dc.dataclass(
            self.model, kw_only=self.kw_only, slots=slots
        )

        setattr(self.model, "__class_getitem__", _struct_getitem(self))
        if self.is_union:
            # install a hook
            self._union_hook: UnionHook[_ModelT] = (hook_cls or UnionHook)(self)
            setattr(self.model, "__init__", _union_init(self._union_hook))
            setattr(self.model, "__setattr__", _union_setattr(self._union_hook))
        if self.has_option(S_ADD_BYTES):
            setattr(self.model, "__bytes__", _struct_bytes(self))

    @override
    def __type__(self) -> type[_ModelT]:
        return self.model

    @override
    def _prepare_fields(self) -> dict[str, Any]:
        # We will inspect all base classes in reverse order and selectively
        # utilize classes that store a struct instance. Beginning at position
        # -1, concluding at 0, and using a step size of -1:
        for candidate in self.model.__mro__[-1:0:-1]:
            if hasstruct(candidate):
                # Importing all fields instead of the entire struct.
                # The default behavior on importing structs is implemented
                # by the Sequence class.
                self += candidate.__struct__  # pyright: ignore[reportOperatorIssue]

        eval_str: bool = self.has_option(S_EVAL_ANNOTATIONS)
        # The why is described in detail here: https://docs.python.org/3/howto/annotations.html
        return inspect.get_annotations(self.model, eval_str=eval_str)

    @override
    def _set_default(self, name: str, value: Any) -> None:
        setattr(self.model, name, value)

    @override
    def _process_default(
        self, name: str, annotation: Any, had_default: bool = False
    ) -> Any:
        default = super()._process_default(name, annotation, had_default)
        if default is INVALID_DEFAULT and had_default:
            self.kw_only = True
        return default

    @override
    def _replace_type(self, name: str, type_: type) -> None:
        self.model.__annotations__[name] = type_

    @override
    def _remove_from_model(self, name: str) -> None:
        self.model.__annotations__.pop(name)
        default = getattr(self.model, name, None)
        # Invisible adds a dataclass.Field to the class definition. We have
        # to remove in order to prevent errors
        if isinstance(default, dc.Field):
            # mitigation for: TypeError: 'XXX' is a field but has no type annotation
            delattr(self.model, name)

    @override
    def unpack_one(self, context: _ContextLike) -> _ModelT:
        return self.model(**super().unpack_one(context))

    @override
    def get_value(self, obj: _ModelT, name: str, field: Field) -> Any | None:
        return getattr(obj, name, None)


# --- private type converter ---
# TODO: documentation
class _StructTypeConverter(registry.TypeConverter):
    def __init__(self) -> None:
        super().__init__()

    @override
    def matches(self, annotation: Any) -> bool:
        return isinstance(annotation, type) and getstruct(annotation) is not None

    @override
    def convert(self, annotation: Any, kwargs: dict[str, Any]) -> _StructLike:
        return getstruct(annotation)  # pyright: ignore[reportReturnType]


registry.annotation_registry.append(_StructTypeConverter())


def _struct_bytes(model: Struct[_ModelT]) -> Callable[[_ModelT], bytes]:
    def to_bytes(self: _ModelT) -> bytes:
        return pack(self, model)

    return to_bytes


P = ParamSpec("P")


def _struct_getitem(
    model: Struct[_ModelT],
) -> Callable[P, Field[Collection[_ModelT], Collection[_ModelT]]]:
    def class_getitem(*args: P.args, **kwargs: P.kwargs):
        dim: int = 1
        # REVISIT: check args
        match len(args):
            case 2:
                _, dim = args  # pyright: ignore[reportAssignmentType]
            case 1:
                (dim,) = args  # pyright: ignore[reportAssignmentType]
            case _:
                raise InvalidValueError(f"Expected only one paremeter, got: {args!r}")

        return Field(model)[dim]

    return class_getitem


# TODO: docs
def Invisible(*, init: bool = False, default: Any = None) -> Any:
    """Create a dataclass field that is hidden from the generated constructor.

    This helper returns a ``dataclasses.field`` configured so that the
    associated attribute is not exposed as a parameter in the dataclass
    ``__init__`` method. It is primarily intended for use in ``@struct``
    definitions where certain fields (e.g., padding, metadata, or internally
    managed values) should exist in the structure layout but must not be
    user-provided during instantiation.

    When used, type checkers and IDEs will treat the field as non-existent
    from the constructor's perspective, while the field still participates in
    the dataclass definition and underlying structure handling.

    >>> @struct
    ... class Format:
    ...     a: uint32_t
    ...     b: f[bytes, b"const value"] = Invisible()

    In this example, field ``b`` is part of the structure definition but is
    not visible as an argument when constructing ``Format``.

    :param init: Whether the field should be included in the generated
        ``__init__`` method. This is typically set to ``False`` to hide the
        field, defaults to False
    :type init: bool, optional
    :param default: Default value assigned to the field if not explicitly set,
        defaults to None
    :type default: Any, optional
    :return: A configured ``dataclasses.field`` instance with ``kw_only=True``
        and the specified visibility settings
    :rtype: Any
    """
    return dc.field(init=init, default=default, kw_only=True)


class StructDefMixin:
    """Mixin providing convenience methods and typing support for ``@struct`` models.

    This mixin centralizes common wrapper functionality required by structure
    definitions so that individual model classes do not need to import or
    reference low-level packing and unpacking utilities directly.

    It provides:

    - ``cls[...]`` support via ``__class_getitem__`` for defining repeated
      fields using the indexing operator.
    - ``cls.from_bytes(...)`` for constructing instances from raw binary data.
    - ``cls.from_file(...)`` for constructing instances from files.
    - ``obj.to_bytes(...)`` for serializing instances back into binary form.

    The primary purpose of this mixin is to improve ergonomics and satisfy
    static type checkers by exposing these behaviors directly on the model
    class rather than requiring explicit imports of ``pack``/``unpack`` helpers.
    """

    __struct__: ClassVar[Struct[Self]]
    """A reference to the struct model of this class"""

    def __class_getitem__(
        cls: type[_ModelT], dim: _LengthT
    ) -> Field[Collection[_ModelT], Collection[_ModelT]]:
        """Enable ``cls[dim]`` syntax for defining repeated structure fields.

        This method allows structure classes to be indexed using the ``[]``
        operator in order to declare collections of that structure within
        other structures.

        :param dim: The length or dimension of the collection
        :type dim: _LengthT
        :return: A field descriptor representing a collection of the structure
        :rtype: Field[Collection[_ModelT], Collection[_ModelT]]
        """
        return getstruct(cls)[dim]

    @classmethod
    def from_bytes(
        cls: type[_ModelT],
        data: Buffer | _StreamType,
        *,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        **kwargs: Any,
    ) -> _ModelT:
        """Construct an instance from raw binary data or a stream.

        This is a convenience wrapper around the underlying ``unpack``
        function, allowing models to be instantiated directly from bytes
        without importing parsing utilities.

        :param data: Raw bytes or a readable stream containing serialized data
        :type data: Buffer | _StreamType
        :param order: Endianness override for parsing, defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Architecture override for parsing, defaults to None
        :type arch: _ArchLike | None, optional
        :return: Parsed model instance
        :rtype: _ModelT
        """
        return unpack(cls, data, order=order, arch=arch, **kwargs)

    @classmethod
    def from_file(
        cls: type[_ModelT],
        filename: str,
        *,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        **kwargs: Any,
    ) -> _ModelT:
        """Construct an instance from a binary file on disk.

        This is a convenience wrapper around ``unpack_file`` for reading and
        parsing structured data directly from a file path.

        :param filename: Path to the file containing serialized data
        :type filename: str
        :param order: Endianness override for parsing, defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Architecture override for parsing, defaults to None
        :type arch: _ArchLike | None, optional
        :return: Parsed model instance
        :rtype: _ModelT
        """
        return unpack_file(cls, filename, order=order, arch=arch, **kwargs)

    @overload
    def to_bytes(
        self,
        *,
        fp: _StreamType,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        use_tempfile: bool = False,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def to_bytes(
        self,
        *,
        fp: None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        use_tempfile: bool = False,
        **kwargs: Any,
    ) -> bytes: ...
    def to_bytes(
        self,
        *,
        fp: _StreamType | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        use_tempfile: bool = False,
        **kwargs: Any,
    ) -> bytes | None:
        """Serialize the instance into its binary representation.

        If ``fp`` is provided, the binary data is written directly into the
        given stream using ``pack_into``. Otherwise, the binary data is
        returned as a ``bytes`` object using ``pack``.

        :param fp: Writable stream to receive the serialized data. If None,
            the serialized bytes are returned, defaults to None
        :type fp: _StreamType | None, optional
        :param order: Endianness override for serialization, defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Architecture override for serialization, defaults to None
        :type arch: _ArchLike | None, optional
        :param use_tempfile: Whether to use a temporary file during packing,
            defaults to False
        :type use_tempfile: bool, optional
        :return: Serialized bytes if ``fp`` is None, otherwise None
        :rtype: bytes | None
        """
        if fp is not None:
            pack_into(
                self,
                fp,
                use_tempfile=use_tempfile,
                order=order,
                arch=arch,
                **kwargs,
            )
        else:
            return pack(
                self,
                use_tempfile=use_tempfile,
                order=order,
                arch=arch,
                **kwargs,
            )


class struct_factory:
    """Factory responsible for converting plain classes into ``@struct`` models.

    This factory provides decorator-style and direct-call APIs for transforming
    a regular class definition into a fully configured ``Struct`` model. The
    resulting class gains dataclass semantics and structure metadata.

    .. admonition::
        The use of ``@dataclass_transform`` ensures that static type checkers
        understand the transformation and correctly interpret field specifiers
        such as ``dataclasses.field`` and :func:`Invisible`.
    """

    mixin: type[StructDefMixin] = StructDefMixin

    @overload
    @dataclass_transform(field_specifiers=(dc.field, Invisible))
    @staticmethod
    def new(
        ty: type[_ModelT],
        kw_only: Literal[False] = False,
        options: Iterable[_OptionLike] | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> type[_ModelT]: ...
    @overload
    @dataclass_transform(kw_only_default=True, field_specifiers=(dc.field, Invisible))
    @staticmethod
    def new(
        ty: type[_ModelT],
        kw_only: Literal[True] = True,
        options: Iterable[_OptionLike] | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> type[_ModelT]: ...
    @overload
    @dataclass_transform(field_specifiers=(dc.field, Invisible))
    @staticmethod
    def new(
        ty: None = None,
        kw_only: Literal[False] = False,
        options: Iterable[_OptionLike] | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> Callable[[_ModelT], type[_ModelT]]: ...
    @overload
    @dataclass_transform(kw_only_default=True, field_specifiers=(dc.field, Invisible))
    @staticmethod
    def new(
        ty: None = None,
        kw_only: Literal[True] = True,
        options: Iterable[_OptionLike] | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> Callable[[_ModelT], type[_ModelT]]: ...
    @dataclass_transform(field_specifiers=(dc.field, Invisible))
    @staticmethod
    def new(
        ty: type[_ModelT] | None = None,
        kw_only: bool = False,
        options: Iterable[_OptionLike] | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        field_options: Iterable[_OptionLike] | None = None,
    ) -> type[_ModelT] | Callable[[_ModelT], type[_ModelT]]:
        """Decorator or direct constructor for creating a ``Struct`` model.

        This method can be used either as:

        - A decorator: ``@struct(...)``
        - A direct transformer: ``MyStruct = struct(MyClass, ...)``

        The method configures structure-wide options such as byte order,
        architecture, and field-level behaviors, and returns a fully
        initialized model class.

        >>> @struct(order=LittleEndian)
        ... class Format:
        ...     field: f[int, uint32]

        :param ty: The target class to be transformed into a Struct model.
            If None, a decorator function is returned
        :type ty: type[_ModelT] | None, optional
        :param kw_only: Whether generated dataclass fields should be keyword-only,
            defaults to False
        :type kw_only: bool, optional
        :param options: Additional options controlling structure behavior,
            defaults to None
        :type options: Iterable[_OptionLike] | None, optional
        :param order: Global byte order configuration applied to all fields,
            defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Global architecture configuration inferred by fields,
            defaults to None
        :type arch: _ArchLike | None, optional
        :param field_options: Additional options applied at the field level,
            defaults to None
        :type field_options: Iterable[_OptionLike] | None, optional
        :return: A transformed Struct model class, or a decorator if ``ty`` is None
        :rtype: type[_ModelT] | Callable[[_ModelT], type[_ModelT]]
        """

        def wrap(cls: type[_ModelT]) -> type[_ModelT]:
            return struct_factory.make_struct(
                cls,
                order=order,
                arch=arch,
                options=options,
                field_options=field_options,
                kw_only=kw_only,
            )

        if ty is not None:
            return struct_factory.make_struct(
                ty,
                order=order,
                arch=arch,
                options=options,
                field_options=field_options,
                kw_only=kw_only,
            )

        return wrap  # pyright: ignore[reportReturnType]

    @dataclass_transform(field_specifiers=(dc.field, Invisible))
    @staticmethod
    def make_struct(
        ty: type[_ModelT],
        options: Iterable[_OptionLike] | None = None,
        order: _EndianLike | None = None,
        arch: _ArchLike | None = None,
        field_options: Iterable[_OptionLike] | None = None,
        kw_only: bool = False,
        hook_cls: type["UnionHook[_ModelT]"] | None = None,
    ) -> type[_ModelT]:
        """Internal helper that performs the actual Struct model creation.

        This method instantiates a :class:`Struct` object using the provided
        configuration and returns the generated model class.

        :param ty: The base class to transform into a Struct model
        :type ty: type[_ModelT]
        :param options: Additional options controlling structure behavior,
            defaults to None
        :type options: Iterable[_OptionLike] | None, optional
        :param order: Global byte order configuration applied to all fields,
            defaults to None
        :type order: _EndianLike | None, optional
        :param arch: Global architecture configuration inferred by fields,
            defaults to None
        :type arch: _ArchLike | None, optional
        :param field_options: Additional options applied at the field level,
            defaults to None
        :type field_options: Iterable[_OptionLike] | None, optional
        :param kw_only: Whether generated dataclass fields should be keyword-only,
            defaults to False
        :type kw_only: bool, optional
        :param hook_cls: Optional hook class for union handling, defaults to None
        :type hook_cls: type["UnionHook[_ModelT]"] | None, optional
        :return: The generated Struct model class
        :rtype: type[_ModelT]
        """
        s = Struct(
            ty,
            order=order,
            arch=arch,
            options=options,
            field_options=field_options,
            kw_only=kw_only,
            hook_cls=hook_cls,
        )
        return s.model


struct = struct_factory.new

class UnionHook(Generic[_ModelT]):
    """Implementation of a hook to simulate union types.

    It will hook two methods of the target model type: :code:`__init__` and
    :code:`__setattr__`. Because the constructor calls *setattr* for each
    attribute in the model, we have to intercept it before it gets called
    to set an internal status.

    Internally, these two methods will be translated into :meth:`~UnionHook.__model_init__`
    and :meth:`~UnionHook.__model_setattr__`. Therefore, any class that implements
    these two methods can be used as a union hook.
    """

    struct: Struct[_ModelT]
    """The struct reference"""

    max_size: int
    """The static (cached) maximum size of the union"""

    def __init__(self, struct_: Struct[_ModelT]) -> None:
        self.struct = struct_
        # Dynamic size is not allowed and will throw an error here
        self.max_size = sizeof(struct_)
        # These attributes are set by default
        self._processing_: bool = False
        self._model_init_: Callable[..., None] = struct_.model.__init__

    def __enter__(self) -> None:
        # shortcut for disabling permanent attribute refresh during
        # init and refresh phases
        self._processing_ = True

    def __exit__(self, exc_type: type, exc_value: Exception, traceback: TracebackType):
        # This variable MUST be reset afterward
        self._processing_ = False

    def __model_init__(self, obj: _ModelT, *args: Any, **kwargs: Any) -> None:
        # since it is possible now, to specify non-kw_only constructors,
        # we have to capture both, args and kwargs
        with self:
            return self._model_init_(obj, *args, **kwargs)

    def __model_setattr__(self, obj: _ModelT, key: str, new_value: Any) -> None:
        # The target attribute will alyaws be set
        object.__setattr__(obj, key, new_value)

        members = self.struct.get_members()
        if self._processing_ or key not in members:
            # Refresh can't be done if:
            #   1) the current instance is alredy being processed
            #   2) the member is not in the internal model
            return

        with self:
            # delegation into method allows for customisation
            self.refresh(obj, key, new_value, members)

    def refresh(
        self, obj: _ModelT, key: str, new_value: Any, members: dict[str, Field]
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
            stream.seek(0)  # pyright: ignore[reportUnusedCallResult]


def _union_init(hook: UnionHook[_ModelT]) -> Callable[..., None]:
    # wrapper function to capture the calling instance
    def init(self: _ModelT, *args: P.args, **kwargs: P.kwargs) -> None:
        return hook.__model_init__(self, *args, **kwargs)

    return init


def _union_setattr(hook: UnionHook[_ModelT]) -> Callable[..., None]:
    # wrapper function to capture the calling instance
    def setattribute(self: _ModelT, key: str, value: Any) -> None:
        hook.__model_setattr__(self, key, value)

    return setattribute


@overload
@dataclass_transform(field_specifiers=(dc.field, Invisible))
def union(
    cls: None = None,
    /,
    *,
    options: Iterable[_OptionLike] | None = None,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    field_options: Iterable[_OptionLike] | None = None,
    kw_only: bool = False,
    hook_cls: type[UnionHook[_ModelT]] | None = None,
) -> Callable[[type[_ModelT]], type[_ModelT]]: ...
@overload
@dataclass_transform(field_specifiers=(dc.field, Invisible))
def union(
    cls: type[_ModelT],
    /,
    *,
    options: Iterable[_OptionLike] | None = None,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    field_options: Iterable[_OptionLike] | None = None,
    kw_only: bool = False,
    hook_cls: type[UnionHook[_ModelT]] | None = None,
) -> type[_ModelT]: ...
@dataclass_transform(field_specifiers=(dc.field, Invisible))
def union(
    cls: type[_ModelT] | None = None,
    /,
    *,
    options: Iterable[_OptionLike] | None = None,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    field_options: Iterable[_OptionLike] | None = None,
    kw_only: bool = False,
    hook_cls: type[UnionHook[_ModelT]] | None = None,
) -> type[_ModelT] | Callable[[type[_ModelT]], type[_ModelT]]:
    """
    Decorator to create a Union class.

    :param cls: The target class used as the base model.
    :param options: Additional options specifying what to include in the final class.
    :param order: Optional configuration value for the byte order of a field.
    :param arch: Global architecture definition (will be inferred on all fields).

    :return: The created Union class or a wrapper function if cls is not provided.
    """
    options = set(list(options or []) + [S_UNION])

    def wrap(cls: type[_ModelT]) -> type[_ModelT]:
        return struct_factory.make_struct(
            cls,
            order=order,
            arch=arch,
            options=options,
            field_options=field_options,
            kw_only=kw_only,
            hook_cls=hook_cls,
        )

    if cls is not None:
        return struct_factory.make_struct(
            cls,
            order=order,
            arch=arch,
            options=options,
            field_options=field_options,
            kw_only=kw_only,
            hook_cls=hook_cls,
        )

    return wrap


@overload
def pack(
    obj: _ContainsStruct[_IT, _OT],
    struct: None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes: ...
@overload
def pack(
    # fallback to allow arbitrary objects
    obj: object,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> bytes: ...
@overload
def pack(
    obj: _IT,
    struct: _SupportsPack[_IT],
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes: ...
@overload
def pack(
    obj: _IT,
    # support arbitrary struct types
    struct: type[_IT],
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes: ...


# @overload
# def pack(
#     obj: _IT,
#     struct: _ContainsStruct[_IT, _OT],
#     /,
#     **kwargs: Any,
# ) -> bytes: ...
def pack(
    obj: _IT | _ContainsStruct[_IT, _OT],
    struct: _SupportsPack[_IT] | type[_IT] | _ContainsStruct[_IT, _OT] | None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwargs: Any,
) -> bytes:
    """
    Pack an object into a bytes buffer using the specified struct.

    :param obj: The object to pack.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: The packed bytes.
    """
    buffer = BytesIO()
    pack_into(  # pyright: ignore[reportCallIssue]
        obj,
        buffer,
        struct,  # pyright: ignore[reportArgumentType]
        order=order,
        arch=arch,
        use_tempfile=use_tempfile,
        as_field=as_field,
        **kwargs,
    )
    return buffer.getvalue()


@overload
def pack_into(
    obj: _ContainsStruct[_IT, _OT],
    buffer: _StreamType,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: object,
    buffer: _StreamType,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: _SupportsPack[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: type[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None: ...
@overload
def pack_into(
    obj: _IT,
    buffer: _StreamType,
    struct: _ContainsStruct[_IT, _OT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None: ...
def pack_into(
    obj: _IT | _ContainsStruct[_IT, _OT],
    buffer: _StreamType,
    struct: type[_IT] | _ContainsStruct[_IT, _OT] | _SupportsPack[_IT] | None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None:
    """
    Pack an object into the specified buffer using the specified struct.

    This function serializes an object (`obj`) into a given buffer, using
    a struct to define how the object should be packed. Optionally, the
    function can handle temporary files for packing, use a `Field` wrapper
    around the struct, and support additional keyword arguments. The packed
    data is written to the `buffer`.

    Example 1: Packing an object into a bytes buffer

    >>> buffer = BytesIO()
    >>> my_obj = SomeObject()  # Assume SomeObject is a valid object to be packed
    >>> pack_into(my_obj, buffer, struct=SomeStruct())  # Using a specific struct
    >>> buffer.getvalue()
    b"..."

    Example 2: Packing into a file-like stream (e.g., file)

    >>> with open('packed_data.bin', 'wb') as f:
    ...     pack_into(my_obj, f, struct=SomeStruct())  # Pack into a file

    Example 3: Using `as_field` to wrap the struct in a Field before packing

    >>> buffer = BytesIO()
    >>> pack_into(42, buffer, struct=uint8, as_field=True)
    >>> buffer.getvalue()
    b"\\x2a"

    :param obj: The object to pack (could be a plain object or a structure-like object).
    :param buffer: The buffer to pack the object into (a writable stream such as `BytesIO` or a file).
    :param struct: The struct to use for packing. If not specified, will infer from `obj`.
    :param use_tempfile: Whether to use a temporary file for packing (experimental).
    :param as_field: Whether to wrap the struct in a `Field` before packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :raises TypeError: If no `struct` is specified and cannot be inferred from the object.
    """
    # fmt: off
    offsets: OrderedDict[int, int] = OrderedDict()
    # NOTE: we don't have to set _root here because the default root context
    # will be this instance.
    context = (O_CONTEXT_FACTORY.value or Context)(
        _parent=None,
        _path="<root>",
        _pos=0,
        _offsets=offsets,
        _is_seq=False,
        _order=order or O_DEFAULT_ENDIAN.value or LittleEndian,
        _arch=arch or O_DEFAULT_ARCH.value or system_arch,
        mode=MODE_PACK,
        **kwds,
    )
    if struct is None:
        struct = getstruct(obj)
    elif as_field:
        struct = Field(struct)  # pyright: ignore[reportArgumentType]
    elif hasstruct(struct):
        struct = getstruct(struct)

    if struct is None:
        raise TypeError("struct must be specified")

    if not hasattr(struct, ATTR_PACK):
        raise TypeError(
            f"pack* called with an unknown struct type ({type(struct)}) - "
            + "no __pack__ defined!"
        )

    prev_order = O_DEFAULT_ENDIAN.value
    prev_arch = O_DEFAULT_ARCH.value
    if order:
        O_DEFAULT_ENDIAN.value = order
    if arch:
        O_DEFAULT_ARCH.value = prev_arch
    try:
        start = 0
        if use_tempfile:
            # NOTE: this implementation is exprimental - use this option with caution.
            with TemporaryFile() as stream:
                context[CTX_STREAM] = stream
                struct.__pack__(obj, context)  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]

                for offset, value in offsets.items():
                    stream.seek(start)  # pyright: ignore[reportUnusedCallResult]
                    buffer.write(stream.read(offset - start))
                    buffer.write(value)
                    start = offset
                if len(offsets) == 0:
                    stream.seek(0)  # pyright: ignore[reportUnusedCallResult]
                    copyfileobj(stream, buffer)

        else:
            # Default implementation: We use an in-memory buffer to store all packed
            # elements and then apply all offset-packed objects.
            stream = BytesIO()
            context[CTX_STREAM] = stream
            struct.__pack__(obj, context) # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]

            content = stream.getbuffer()
            if len(offsets) == 0:
                buffer.write(content)
            else:
                for offset, value in offsets.items():
                    buffer.write(content[start:offset])
                    buffer.write(value)
                    start = offset
    finally:
        O_DEFAULT_ENDIAN.value = prev_order
        O_DEFAULT_ARCH.value = prev_arch


@overload
def pack_file(
    obj: _ContainsStruct[_IT, _OT],
    filename: str,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: object,
    filename: str,
    struct: None = None,
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: _SupportsPack[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: type[_IT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
@overload
def pack_file(
    obj: _IT,
    filename: str,
    struct: _ContainsStruct[_IT, _OT],
    /,
    *,
    use_tempfile: bool = ...,
    as_field: bool = ...,
    order: _EndianLike | None = ...,
    arch: _ArchLike | None = ...,
    **kwds: Any,
) -> None: ...
def pack_file(
    obj: _IT | _ContainsStruct[_IT, _OT],
    filename: str,
    struct: _SupportsPack[_IT] | type[_IT] | _ContainsStruct[_IT, _OT] | None = None,
    /,
    *,
    use_tempfile: bool = False,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> None:
    """
    Pack an object into a file using the specified struct.

    :param obj: The object to pack.
    :param filename: The name of the file to write to.
    :param struct: The struct to use for packing.
    :param kwds: Additional keyword arguments to pass to the pack function.

    :return: None
    """
    with open(filename, "w+b") as fp:
        pack_into(  # pyright: ignore[reportCallIssue]
            obj,
            fp,
            struct,  # pyright: ignore[reportArgumentType]
            use_tempfile=use_tempfile,
            as_field=as_field,
            order=order,
            arch=arch,
            **kwds,
        )


@overload
def unpack(
    struct: _ContainsStruct[_IT, _OT],
    buffer: Buffer | _StreamType,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack(
    struct: _SupportsUnpack[_OT],
    buffer: Buffer | _StreamType,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack(
    struct: type[_OT],
    buffer: Buffer | _StreamType,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
def unpack(
    struct: type[_OT] | _SupportsUnpack[_OT] | _ContainsStruct[_IT, _OT],
    buffer: Buffer | _StreamType,
    /,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT:
    """
    Unpack an object from a bytes buffer or stream using the specified struct.

    This function takes a `struct` that defines how data should be unpacked,
    a `buffer` (either bytes or a stream) containing the serialized data, and
    returns the unpacked object. If `as_field` is set to True, the `struct` is
    wrapped by a `Field`. Additional keyword arguments are passed to the root
    context as attributes.

    Example:

    >>> buffer = b'\\x00\\x01\\x02\\x03'
    >>> struct = SomeStruct()
    >>> unpack(struct, buffer)
    ...

    :param struct: The struct to use for unpacking (could be a `SupportsUnpack` or `ContainsStruct` object).
    :param buffer: The bytes buffer or stream to unpack from.
    :param as_field: Whether to wrap the struct in a `Field` transformer before unpacking.
    :param kwds: Additional keyword arguments to pass to the unpack function.

    :return: The unpacked object, which is the result of calling `struct.__unpack__(context)`.

    :raises TypeError: If the `struct` is not a valid struct instance.
    """
    # fmt: off
    # prepare the data stream
    stream = buffer if isinstance(buffer, IOBase) else BytesIO(buffer)
    context = (O_CONTEXT_FACTORY.value or Context)(
        _path="<root>",
        _parent=None,
        _io=stream,
        _pos=0,
        _is_seq=False,
        _order=order or O_DEFAULT_ENDIAN.value or LittleEndian,
        _arch=arch or O_DEFAULT_ARCH.value or system_arch,
        mode=MODE_UNPACK,
        **kwds,
    )
    if as_field:
        struct = Field(struct)  # pyright: ignore[reportArgumentType]
    elif hasstruct(struct):
        struct = getstruct(struct)

    if not isinstance(struct, _SupportsUnpack):
        raise TypeError(f"{type(struct).__name__} is not a valid struct instance!")

    prev_order = O_DEFAULT_ENDIAN.value
    prev_arch = O_DEFAULT_ARCH.value
    if order:
        O_DEFAULT_ENDIAN.value = order
    if arch:
        O_DEFAULT_ARCH.value = arch

    try:
        return struct.__unpack__(context)
    finally:
        O_DEFAULT_ARCH.value = prev_arch
        O_DEFAULT_ENDIAN.value = prev_order


@overload
def unpack_file(
    struct: _ContainsStruct[_IT, _OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack_file(
    struct: _SupportsUnpack[_OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
@overload
def unpack_file(
    struct: type[_OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
) -> _OT: ...
def unpack_file(
    struct: type[_OT] | _SupportsUnpack[_OT] | _ContainsStruct[_IT, _OT],
    filename: str,
    /,
    *,
    as_field: bool = False,
    order: _EndianLike | None = None,
    arch: _ArchLike | None = None,
    **kwds: Any,
):
    """
    Unpack an object from a file using the specified struct.

    :param struct: The struct to use for unpacking.
    :param filename: The name of the file to read from.
    :param kwds: Additional keyword arguments to pass to the unpack function.

    :return: The unpacked object.
    """
    with open(filename, "rb") as fp:
        return unpack(struct, fp, as_field=as_field, arch=arch, order=order, **kwds)


@overload
def sizeof(obj: _SupportsSize, **kwds: Any) -> int: ...
@overload
def sizeof(obj: _ContainsStruct, **kwds: Any) -> int: ...
@overload
def sizeof(obj: type, **kwds: Any) -> int: ...
def sizeof(obj: _SupportsSize | _ContainsStruct | type, **kwds: Any) -> int:
    context = (O_CONTEXT_FACTORY.value or Context)(_parent=None, _path="<root>", **kwds)
    struct_ = obj
    if hasstruct(struct_):
        struct_ = getstruct(struct_)

    if not isinstance(struct_, _SupportsSize):
        raise TypeError(f"{type(struct_).__name__} does not support size calculation!")

    size = struct_.__size__(context)
    if not isinstance(size, int):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise DynamicSizeError(f"Struct {struct_} is using a dynamic size ", context)
    return size
