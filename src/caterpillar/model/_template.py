# pylint: disable=protected-access
# pyright: reportAny=false, reportExplicitAny=false
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
import sys
import inspect
import types
import dataclasses

from hashlib import md5
from types import ModuleType
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    TypeVar,
    get_args,
    get_origin,
)
from typing_extensions import overload, override, dataclass_transform

from caterpillar.fields import Field, INVALID_DEFAULT
from caterpillar.model import Invisible, Struct
from caterpillar.options import S_UNION
from caterpillar.shared import ATTR_TEMPLATE, hasstruct, typeof
from caterpillar.abc import (
    _LengthT,
    _StructLike,
    _ContextLambda,
    _GreedyType,
    _SwitchLambda,
    _EndianLike,
    _ArchLike,
)


_TYPEVAR_TYPE: type[TypeVar] = type(TypeVar("_CaterpillarTemplateTypeVar"))


class TemplateTypeVar:
    """Template type variable.

    These specialised type variables are used within a template definition. They
    support most field operators. Therefore, they can be used in some situations
    where you need to adapt the field type at runtime.

    >>> T = TemplateTypeVar("T")

    Note that there is currently no support for inlined type variables, for example:

    >>> @template(T)
    ... class Foo:
    ...     bar: Enum(Baz, T) # !!! throws an error

    is not possible.
    """

    name: str
    """The bound name of this type variable"""

    field_kwds: dict[str, Any]
    """Arguments that will be passed to the created field instance."""

    def __init__(self, name: str, **field_kwds: Any) -> None:
        self.name = name
        self.field_kwds = field_kwds or {}

    @override
    def __repr__(self) -> str:
        # This method is important for documentation and type hints.
        # We try to illustrate the generic type as good as possible.
        count = self.field_kwds.get("amount")
        if not count:
            return f"~{self.name}"

        # display sequence access brackets
        return f"~{self.name}[{count}]"

    # Now we have to implement all special operators defined in FieldMixin
    def __getitem__(self, amount: _LengthT) -> "TemplateTypeVar":
        return TemplateTypeVar(self.name, amount=amount, **self.field_kwds)

    def __rshift__(
        self, switch: _SwitchLambda | dict[str, _StructLike]
    ) -> "TemplateTypeVar":
        return TemplateTypeVar(self.name, options=switch, **self.field_kwds)

    def __matmul__(self, offset: int | _ContextLambda[int]) -> "TemplateTypeVar":
        return TemplateTypeVar(self.name, offset=offset, **self.field_kwds)

    def __set_byteorder__(self, order: _EndianLike) -> "TemplateTypeVar":
        return TemplateTypeVar(self.name, order=order, **self.field_kwds)

    def __rsub__(self, bits: int | _ContextLambda[int]) -> "TemplateTypeVar":
        return TemplateTypeVar(self.name, bits=bits, **self.field_kwds)

    # @scheduled_for_removal
    def __floordiv__(self, condition: bool | _ContextLambda[bool]) -> "TemplateTypeVar":
        return TemplateTypeVar(self.name, condition=condition, **self.field_kwds)

    def to_field(
        self,
        struct: _StructLike | _ContextLambda,
        arch: _ArchLike | None = None,
        default: Any = INVALID_DEFAULT,
    ) -> Field:
        # REVISIT: what about flags?
        if get_origin(struct) is Annotated:
            return struct

        return Field(struct, arch=arch, default=default, **self.field_kwds)


class TemplateFieldRef:
    """Field metadata for Python ``TypeVar`` based templates."""

    param: TypeVar
    field_kwds: dict[str, Any]

    def __init__(self, param: TypeVar, **field_kwds: Any) -> None:
        self.param = param
        self.field_kwds = field_kwds or {}

    @override
    def __repr__(self) -> str:
        name = getattr(self.param, "__name__", repr(self.param))
        count = self.field_kwds.get("amount")
        if not count:
            return f"field_of({name})"
        return f"field_of({name})[{count}]"

    def __getitem__(self, amount: _LengthT) -> "TemplateFieldRef":
        return TemplateFieldRef(self.param, amount=amount, **self.field_kwds)

    def __rshift__(
        self, switch: _SwitchLambda | dict[str, _StructLike]
    ) -> "TemplateFieldRef":
        return TemplateFieldRef(self.param, options=switch, **self.field_kwds)

    def __matmul__(self, offset: int | _ContextLambda[int]) -> "TemplateFieldRef":
        return TemplateFieldRef(self.param, offset=offset, **self.field_kwds)

    def __set_byteorder__(self, order: _EndianLike) -> "TemplateFieldRef":
        return TemplateFieldRef(self.param, order=order, **self.field_kwds)

    def __rsub__(self, bits: int | _ContextLambda[int]) -> "TemplateFieldRef":
        return TemplateFieldRef(self.param, bits=bits, **self.field_kwds)

    def __floordiv__(
        self, condition: bool | _ContextLambda[bool]
    ) -> "TemplateFieldRef":
        return TemplateFieldRef(self.param, condition=condition, **self.field_kwds)

    def with_param(self, param: TypeVar) -> "TemplateFieldRef":
        return TemplateFieldRef(param, **self.field_kwds)

    def to_field(
        self,
        struct: _StructLike | _ContextLambda,
        default: Any = INVALID_DEFAULT,
    ) -> Field:
        if get_origin(struct) is Annotated:
            _, struct, *_ = get_args(struct)

        return Field(struct, default=default, **self.field_kwds)


def field_of(param: Any) -> TemplateFieldRef:
    """Create layout metadata for a Python ``TypeVar`` template field.

    ..versionadded:: 2.9.0
    """
    return TemplateFieldRef(param)


def get_caller_module(frame: int = 1) -> str:
    try:
        # Direct call to retrieve the module name
        return sys._getframemodulename(frame) or "__main__"
    except AttributeError:
        # Sometimes the call fails and we have to navigate manually
        try:
            return sys._getframe(frame).f_globals.get("__name__", "__main__")
        except (AttributeError, ValueError):
            # Use inspect module instead
            pass
    try:
        stack = inspect.stack()[frame]
        return stack.frame.f_globals.get("__name__", "__main__")
    except (AttributeError, ValueError) as e:
        raise ModuleNotFoundError("Could not load module from caller!") from e


@dataclasses.dataclass
class TemplateInfo:
    required_tys: dict[str, Any]
    positional_tys: dict[str, Any]

    def is_defined(self, name: str) -> bool:
        return name in list(self.required_tys) + list(self.positional_tys)

    def add_required(self, name: str) -> None:
        if self.is_defined(name):
            raise ValueError(f"Typename {name!r} already defined!")
        self.required_tys[name] = None

    def add_positional(self, name: str, default: Any | None = None) -> None:
        if self.is_defined(name):
            raise ValueError(f"Typename {name!r} already defined!")
        self.positional_tys[name] = default


@dataclasses.dataclass
class GenericTemplateInfo:
    parameters: tuple[TypeVar, ...]
    cache: dict[tuple[str, ...], type] = dataclasses.field(default_factory=dict)


def istemplate(obj: object) -> bool:
    """Return true if the object is a template."""
    return hasattr(obj, ATTR_TEMPLATE)


_TemplateModelT = TypeVar("_TemplateModelT")


def _is_typevar(value: Any) -> bool:
    return isinstance(value, _TYPEVAR_TYPE)


def _replace_typevars(value: Any, bindings: dict[Any, Any]) -> Any:
    if _is_typevar(value):
        replacement = bindings.get(value, value)
        if _is_typevar(replacement):
            return replacement
        return typeof(replacement) if not isinstance(replacement, type) else replacement

    origin = get_origin(value)
    if origin is None:
        return value

    args = get_args(value)
    if not args:
        return value

    if origin is Annotated:
        type_hint, *metadata = args
        return Annotated[
            (
                _replace_typevars(type_hint, bindings),
                *(_replace_typevars(item, bindings) for item in metadata),
            )
        ]

    replaced_args = tuple(_replace_typevars(arg, bindings) for arg in args)
    try:
        return origin[replaced_args]
    except TypeError:
        return value


def _resolve_generic_marker(
    marker: Any,
    bindings: dict[Any, Any],
    default: Any,
) -> Any:
    if isinstance(marker, TemplateFieldRef):
        replacement = bindings.get(marker.param, marker.param)
        if _is_typevar(replacement):
            return marker.with_param(replacement)
        return marker.to_field(replacement, default=default)

    if _is_typevar(marker):
        replacement = bindings.get(marker, marker)
        if _is_typevar(replacement):
            return replacement

        if get_origin(replacement) is Annotated:
            return replacement

        return Field(replacement, default=default)

    return _replace_typevars(marker, bindings)


def _specialize_generic_annotation(
    annotation: Any,
    bindings: dict[Any, Any],
    default: Any,
) -> Any:
    if get_origin(annotation) is Annotated:
        type_hint, marker, *extra = get_args(annotation)
        return Annotated[
            (
                _replace_typevars(type_hint, bindings),
                _resolve_generic_marker(marker, bindings, default),
                *(_replace_typevars(item, bindings) for item in extra),
            )
        ]
    return _resolve_generic_marker(annotation, bindings, default)


def _generic_name(origin: type, args: tuple[Any, ...], partial: bool) -> str:
    suffix = get_mangled_name(origin, {str(arg): "" for arg in args})
    template_suffix = "Partial" if partial else "Struct"
    return f"{suffix}_{template_suffix}"


def _create_generic_template(
    cls: type[_TemplateModelT],
    parameters: tuple[Any, ...] | None = None,
) -> type[_TemplateModelT]:
    params = tuple(parameters or getattr(cls, "__parameters__", ()))
    if not params:
        raise TypeError("Generic template class needs at least one type parameter")

    def class_getitem(template_cls: type, args: Any) -> type:
        return _derive_generic_template(
            template_cls,
            *((args,) if not isinstance(args, tuple) else args),
            allow_partial=True,
            module_name=template_cls.__module__,
        )

    setattr(cls, ATTR_TEMPLATE, GenericTemplateInfo(params))
    setattr(cls, "__class_getitem__", classmethod(class_getitem))
    return cls


def _collect_generic_args(
    info: GenericTemplateInfo,
    tys_args: tuple[Any, ...],
    tys_kwargs: dict[str, Any],
    partial: bool,
) -> tuple[Any, ...]:
    if len(tys_args) > len(info.parameters):
        raise ValueError(
            f"Expected max. {len(info.parameters)} positional arguments - got {len(tys_args)}!"
        )

    args: list[Any | None] = [None] * len(info.parameters)
    for index, value in enumerate(tys_args):
        args[index] = value

    param_names = {param.__name__: index for index, param in enumerate(info.parameters)}
    for name, value in tys_kwargs.items():
        if name not in param_names:
            raise ValueError(f"Unknown type argument: {name!r}")
        index = param_names[name]
        if args[index] is not None:
            raise ValueError(f"Type argument {name!r} already defined!")
        args[index] = value

    for index, value in enumerate(args):
        if value is not None:
            continue
        if partial:
            args[index] = info.parameters[index]
            continue
        name = info.parameters[index].__name__
        raise ValueError(f"Missing required type argument: {name!r}")

    return tuple(args)


@overload
@dataclass_transform(field_specifiers=(dataclasses.field, Invisible))
def template(
    cls: str | TemplateTypeVar | TypeVar | None = None,
    *args: str | TemplateTypeVar | type[_TemplateModelT] | TypeVar,
    **kwargs: str | TemplateTypeVar | TypeVar,
) -> Callable[[type[_TemplateModelT]], type[_TemplateModelT]]: ...
@overload
@dataclass_transform(field_specifiers=(dataclasses.field, Invisible))
def template(
    cls: type[_TemplateModelT],
    *args: str | TemplateTypeVar | type[_TemplateModelT] | TypeVar,
    **kwargs: str | TemplateTypeVar | TypeVar,
) -> type[_TemplateModelT]: ...
@dataclass_transform(field_specifiers=(dataclasses.field, Invisible))
def template(
    cls: str | TemplateTypeVar | type[_TemplateModelT] | TypeVar | None = None,
    *args: str | TemplateTypeVar | type[_TemplateModelT] | TypeVar,
    **kwargs: str | TemplateTypeVar | TypeVar,
) -> Callable[[type[_TemplateModelT]], type[_TemplateModelT]]:
    """
    Defines required template type variables if necessary and prepares
    template class definition.

    :return: a wrapper function that will be called with the class instance
    :rtype: Callable[[type], type]
    """
    if isinstance(cls, type):
        return _create_generic_template(cls)

    if cls is not None:
        args = (cls,) + args

    if len(args) == 0 and len(kwargs) == 0:
        raise ValueError("Template class needs at least one template type var")

    info: TemplateInfo = TemplateInfo({}, {})
    module: ModuleType = sys.modules[get_caller_module(frame=2)]
    disposable: list[str] = []
    for value in args:
        var: TemplateTypeVar
        match value:
            case str():
                info.add_required(value)
                var = TemplateTypeVar(value)
            case TemplateTypeVar():
                info.add_required(value.name)
                var = value
            case _:
                raise TypeError(f"Invalid typename type: {value!r}")

        # the type variable will be set globally (at least for
        # class creation)
        if not hasattr(module, var.name):
            setattr(module, var.name, var)
            disposable.append(var.name)

    for name, value in kwargs.items():
        # ellipsis indicates no default value
        if isinstance(value, _GreedyType):
            value = None

        info.add_positional(name, value)
        if not hasattr(module, name):
            setattr(module, name, TemplateTypeVar(name))
            disposable.append(name)

    # the class will get special attributes that identify it as
    # a template class
    def create_template_class(cls: type[_TemplateModelT]) -> type[_TemplateModelT]:
        cls.__annotations__ = inspect.get_annotations(cls, eval_str=True)
        for name in disposable:
            # Only temporary template vars will be removed
            delattr(module, name)
        setattr(cls, ATTR_TEMPLATE, info)
        return cls

    return create_template_class


def get_mangled_name(model_ty: type, annotations: dict[str, Any]) -> str:
    ty_name = model_ty.__name__
    parts: list[str] = []
    for name, value in annotations.items():
        parts.append(str(f"{name}{value!r}"))

    hex_name = md5("".join(parts).encode()).hexdigest()
    return f"_{hex_name}{ty_name}"


def _derive_generic_template(
    template_ty: type,
    *tys_args: TypeVar | str,
    partial: bool = False,
    allow_partial: bool = False,
    name: str | _GreedyType | None = None,
    union: bool = False,
    module_name: str | None = None,
    **tys_kwargs: Any,
) -> type:
    info: GenericTemplateInfo = getattr(template_ty, ATTR_TEMPLATE)
    args = _collect_generic_args(
        info,
        tys_args,
        tys_kwargs,
        partial=partial or allow_partial,
    )
    remaining = tuple(arg for arg in args if _is_typevar(arg))
    is_partial = bool(remaining)
    if is_partial and not (partial or allow_partial):
        raise ValueError(f"Missing required type argument: {remaining[0].__name__!r}")

    key = tuple(repr(arg) for arg in args)
    cached = info.cache.get(key)
    if cached is not None and name is None and not union:
        return cached
    should_cache = name is None and not union

    if isinstance(name, _GreedyType):
        name = None

    class_name = name or _generic_name(template_ty, args, is_partial)
    module = module_name or template_ty.__module__
    bindings = dict(zip(info.parameters, args))
    annotations = inspect.get_annotations(template_ty, eval_str=True)
    new_annotations = {
        field_name: _specialize_generic_annotation(
            annotation,
            bindings,
            getattr(template_ty, field_name, INVALID_DEFAULT),
        )
        for field_name, annotation in annotations.items()
    }

    def body(namespace: dict[str, Any]) -> None:
        namespace["__module__"] = module
        namespace["__annotations__"] = new_annotations
        namespace["__origin__"] = template_ty
        namespace["__args__"] = args

    bases = tuple(base for base in template_ty.__bases__ if base is not Generic)
    if remaining:
        bases = bases + (
            Generic[remaining[0]] if len(remaining) == 1 else Generic[remaining],
        )
    bases = bases or (object,)

    new_ty = types.new_class(
        class_name,
        bases,
        {},
        body,
    )
    if is_partial:
        _create_generic_template(new_ty, remaining)
        if should_cache:
            info.cache[key] = new_ty
        return new_ty

    struct_ty = Struct(new_ty, options={} if not union else {S_UNION}).model
    if should_cache:
        info.cache[key] = struct_ty
    return struct_ty


def derive(
    template_ty: type,
    *tys_args: _StructLike,
    partial: bool = False,
    name: str | _GreedyType | None = None,
    union: bool = False,
    **tys_kwargs: _StructLike,
) -> type:
    """Creates a new struct class based on the given template class.

    :param template_ty: the template class
    :type template_ty: type
    :param partial: whether the resulting class is also a template, defaults to False
    :type partial: bool, optional
    :param name: the new class name, :code:`...` infers the outer variable name, defaults to None
    :type name: str | Ellipsis, optional
    :return: the derived type
    :rtype: type
    """
    if hasstruct(template_ty) and not tys_args and not tys_kwargs:
        return template_ty

    if not istemplate(template_ty):
        raise TypeError(f"{template_ty.__name__} is not a template class!")

    info: TemplateInfo = getattr(template_ty, ATTR_TEMPLATE)
    if isinstance(info, GenericTemplateInfo):
        if isinstance(name, _GreedyType):
            try:
                frame = sys._getframe(1)
                context = inspect.getframeinfo(frame).code_context[0]
                if context.count("=") != 0:
                    parts = context.split(" = ")
                    if len(parts) >= 2:
                        name = parts[0]
            except (AttributeError, KeyError, IndexError, TypeError):
                pass
        return _derive_generic_template(
            template_ty,
            *tys_args,
            partial=partial,
            name=name,
            union=union,
            module_name=get_caller_module(2),
            **tys_kwargs,
        )

    if len(tys_args) == 0 and len(tys_kwargs) == 0:
        has_defaults = any(value is not None for value in info.positional_tys.values())
        if not has_defaults:
            raise ValueError(
                (
                    "To derive a class from a template class at least one "
                    "type argument must be given!"
                )
            )
    if len(tys_args) > len(info.required_tys):
        raise ValueError(
            f"Expected max. {len(info.required_tys)} positional arguments - got {len(tys_args)}!"
        )

    # update necessary parameters
    required_tys = [x for x in info.required_tys if not info.required_tys[x]]
    for arg_name, value in zip(required_tys[: len(tys_args)], tys_args):
        tys_kwargs[arg_name] = value

    # validate against required type parameters
    if not partial:
        for arg_name, value in info.required_tys.items():
            if arg_name not in tys_kwargs and value is None:
                raise ValueError(f"Missing required type argument: {arg_name!r}")

    if isinstance(name, _GreedyType):
        try:
            # Just a hacky way of getting the variable name if possible
            frame = sys._getframe(1)
            context = inspect.getframeinfo(frame).code_context[0]
            if context.count("=") != 0:
                # definition must be <name> = <...>
                parts = context.split(" = ")
                if len(parts) >= 2:
                    name = parts[0]
        except (AttributeError, KeyError, IndexError, TypeError):
            pass

    if name is None:
        name = get_mangled_name(template_ty, tys_kwargs)

    # IF the target module already stores the new type, then return it
    # directly
    module = get_caller_module(2)
    new_ty = getattr(sys.modules[module], name, None)
    if new_ty is None:
        bases = list(template_ty.__bases__)
        for i, base_ty in enumerate(bases):
            if istemplate(base_ty):
                bases[i] = derive(base_ty, *tys_args, *tys_kwargs)

        new_ty = types.new_class(name, template_ty.__bases__, {})

    # prepare annotations
    annotations = inspect.get_annotations(template_ty)
    replaced = {}
    for name, value in annotations.items():
        if isinstance(value, TemplateTypeVar):
            replacement = tys_kwargs.get(value.name)
            if replacement is None:
                replacement = info.positional_tys.get(
                    value.name, info.positional_tys.get(value.name)
                )

            if replacement is None:
                if partial:
                    # missing types will be replaced later on
                    continue

                raise ValueError(
                    f"Could not find type replacement for {value.name!r} at {name!r}"
                )

            if isinstance(replacement, TemplateTypeVar):
                continue

            annotations[name] = value.to_field(
                replacement,
                default=getattr(template_ty, name, INVALID_DEFAULT),
            )
            replaced[value.name] = replacement

    new_ty.__annotations__ = annotations
    new_ty.__module__ = module
    if not partial:
        new_ty.__struct__ = Struct(new_ty, options={} if not union else {S_UNION})
    else:
        new_info = TemplateInfo(info.required_tys.copy(), info.positional_tys.copy())
        for name, replacement in replaced.items():
            if name in info.required_tys:
                new_info.required_tys[name] = replacement
            elif name in info.positional_tys:
                new_info.positional_tys[name] = replacement
        setattr(new_ty, ATTR_TEMPLATE, new_info)
    return new_ty
